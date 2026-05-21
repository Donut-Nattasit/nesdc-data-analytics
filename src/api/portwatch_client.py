import requests
import pandas as pd
import time
from typing import List, Dict, Optional
from src.api.network_utils import resilient_request
from src.api.cache_manager import APICacheManager

class PortWatchClient:
    """
    A resilient client for the IMF PortWatch Search API (OGC API - Records).
    Optimized with exponential backoff retries and local SQLite caching.
    Base URL: https://portwatch.imf.org/api/search/v1
    """

    BASE_URL = "https://portwatch.imf.org/api/search/v1"

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the client with a session and local cache.
        """
        self.session = requests.Session()
        self.cache = APICacheManager(db_path=db_path)

    def get_collections(self) -> List[Dict]:
        """
        List all available data collections.
        """
        url = f"{self.BASE_URL}/collections"
        try:
            response = resilient_request("GET", url, session=self.session)
            response.raise_for_status()
            return response.json().get('collections', [])
        except Exception as e:
            print(f"[PortWatch Client Warning] Failed to fetch PortWatch collections: {e}")
            return []

    def get_collection_details(self, collection_id: str) -> Dict:
        """
        Get metadata for a specific collection.
        """
        url = f"{self.BASE_URL}/collections/{collection_id}"
        try:
            response = resilient_request("GET", url, session=self.session)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[PortWatch Client Warning] Failed to fetch PortWatch collection details for '{collection_id}': {e}")
            return {}

    def get_items(self, collection_id: str, limit: int = 100, offset: int = 0, datetime: Optional[str] = None, filters: Optional[Dict] = None) -> pd.DataFrame:
        """
        Fetch items (records/data points) within a collection.
        """
        url = f"{self.BASE_URL}/collections/{collection_id}/items"
        params = {
            'limit': limit,
            'offset': offset
        }
        if datetime:
            params['datetime'] = datetime
        if filters:
            params.update(filters)

        try:
            response = resilient_request("GET", url, session=self.session, params=params)
            response.raise_for_status()
            data = response.json()
            features = data.get('features', [])
            
            if not features:
                return pd.DataFrame()
            
            # Extract properties from GeoJSON features, including the top-level 'id'
            properties_list = []
            for f in features:
                props = f.get('properties', {}).copy()
                if 'id' not in props and 'id' in f:
                    props['id'] = f['id']
                properties_list.append(props)
            
            df = pd.DataFrame(properties_list)
            return df
        except Exception as e:
            print(f"[PortWatch Client Warning] Failed to fetch items from PortWatch collection '{collection_id}': {e}")
            return pd.DataFrame()

    def get_all_items(self, collection_id: str, datetime: Optional[str] = None, filters: Optional[Dict] = None, max_records: int = 1000, frequency: str = 'daily', force_refresh: bool = False) -> pd.DataFrame:
        """
        Fetch all items with automatic pagination and local caching.
        """
        cache_key = f"portwatch_items_{collection_id}_{datetime or 'all'}_{str(sorted(list((filters or {}).items()))) if filters else ''}"
        
        # Check cache
        cached_df = self.cache.get(cache_key, frequency=frequency, force_refresh=force_refresh)
        if cached_df is not None:
            return cached_df

        # Fetch fresh data
        all_dfs = []
        offset = 0
        limit = 100
        
        while offset < max_records:
            df = self.get_items(collection_id, limit=limit, offset=offset, datetime=datetime, filters=filters)
            if df.empty:
                break
            all_dfs.append(df)
            offset += len(df)
            if len(df) < limit:
                break
            time.sleep(0.1)
            
        if not all_dfs:
            return pd.DataFrame()
            
        df_combined = pd.concat(all_dfs, ignore_index=True)
        
        # Cache results
        if not df_combined.empty:
            self.cache.set(cache_key, df_combined, frequency=frequency)
            
        return df_combined

    def get_data_url(self, item_id: str) -> Optional[str]:
        """
        Get the actual data URL (e.g., ArcGIS FeatureServer) for a given item ID.
        """
        url = f"{self.BASE_URL}/collections/dataset/items/{item_id}"
        try:
            response = resilient_request("GET", url, session=self.session)
            response.raise_for_status()
            data = response.json()
            return data.get('properties', {}).get('url')
        except Exception as e:
            print(f"[PortWatch Client Warning] Failed to fetch data URL for item '{item_id}': {e}")
            return None

    def fetch_arcgis_data(self, feature_server_url: str, layer_id: int = 0, where: str = "1=1", out_fields: str = "*", limit: int = 1000, frequency: str = 'daily', force_refresh: bool = False) -> pd.DataFrame:
        """
        Fetch data from an ArcGIS FeatureServer with automatic pagination and local caching.
        """
        cache_key = f"portwatch_arcgis_{feature_server_url.replace('/', '_')}_{layer_id}_{where}_{out_fields}"
        
        # Check cache
        cached_df = self.cache.get(cache_key, frequency=frequency, force_refresh=force_refresh)
        if cached_df is not None:
            return cached_df

        # Fetch fresh data
        query_url = f"{feature_server_url.strip('/')}/{layer_id}/query"
        params = {
            'where': where,
            'outFields': out_fields,
            'f': 'json',
            'resultRecordCount': limit,
            'resultOffset': 0
        }
        
        all_features = []
        while True:
            try:
                response = resilient_request("GET", query_url, session=self.session, params=params)
                response.raise_for_status()
                data = response.json()
                features = data.get('features', [])
                if not features:
                    break
                all_features.extend([f['attributes'] for f in features])
                
                if len(features) < params['resultRecordCount']:
                    break
                    
                params['resultOffset'] += len(features)
                time.sleep(0.1)
            except Exception as e:
                print(f"[PortWatch Client Warning] Error fetching ArcGIS data: {e}")
                break
                
        if not all_features:
            return pd.DataFrame()
            
        df = pd.DataFrame(all_features)
        
        # Convert dates to datetime objects
        for col in df.columns:
            if 'date' in col.lower():
                if df[col].dtype in ['int64', 'float64']:
                    # ArcGIS uses milliseconds for epoch
                    df[col] = pd.to_datetime(df[col], unit='ms')
                else:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                
        # Cache results
        if not df.empty:
            self.cache.set(cache_key, df, frequency=frequency)
            
        return df

    def get_aggregations(self, collection_id: str) -> Dict:
        """
        Fetch aggregated data for a collection.
        """
        url = f"{self.BASE_URL}/collections/{collection_id}/aggregations"
        try:
            response = resilient_request("GET", url, session=self.session)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[PortWatch Client Warning] Failed to fetch PortWatch aggregations for '{collection_id}': {e}")
            return {}

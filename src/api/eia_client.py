import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv
from src.api.network_utils import resilient_request
from src.api.cache_manager import APICacheManager

class EIAClient:
    """
    A high-performance resilient client for the Energy Information Administration (EIA) API v2.
    Optimized with automatic pagination, exponential backoff retries, and local SQLite caching.
    """

    BASE_URL = "https://api.eia.gov/v2"

    def __init__(self, api_key=None, db_path=None):
        """
        Initialize the client with an API key, session, and local cache.
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("EIA_API_KEY")
        
        if not self.api_key:
            raise ValueError("API key must be provided or set in EIA_API_KEY environment variable.")
        
        self.session = requests.Session()
        self.session.params = {'api_key': self.api_key}
        self.cache = APICacheManager(db_path=db_path)

    def _get_with_pagination(self, url, params):
        """
        Internal helper to handle EIA API v2 pagination (offset/length) resiliently.
        """
        all_data = []
        offset = 0
        length = 5000  # Default max per request
        
        params = params.copy()
        params['length'] = length
        
        while True:
            params['offset'] = offset
            try:
                response = resilient_request("GET", url, session=self.session, params=params)
                response.raise_for_status()
                res_json = response.json().get('response', {})
                data = res_json.get('data', [])
                total = int(res_json.get('total', 0))
                
                if not data:
                    break
                    
                all_data.extend(data)
                offset += len(data)
                
                if offset >= total or len(data) < length:
                    break
                
                # Small delay to be polite to the API if paginating heavily
                time.sleep(0.1)
            except Exception as e:
                print(f"[EIA Client Warning] Pagination error at offset {offset}: {e}")
                break
                
        return all_data

    def get_metadata(self, route=""):
        """
        Fetch metadata for a specific route.
        """
        url = f"{self.BASE_URL}/{route.strip('/')}"
        try:
            response = resilient_request("GET", url, session=self.session)
            response.raise_for_status()
            return response.json().get('response', {})
        except Exception as e:
            print(f"[EIA Client Warning] Failed to fetch EIA metadata for route '{route}': {e}")
            return {}

    def search_routes(self, keyword, start_route="", max_depth=3):
        """
        Recursively search the EIA hierarchy for routes matching a keyword.
        """
        results = []
        keyword = keyword.lower()
        
        def _search(current_route, depth):
            if depth > max_depth:
                return
            
            metadata = self.get_metadata(current_route)
            
            # Check current route name/description
            name = metadata.get('name', '').lower()
            desc = metadata.get('description', '').lower()
            
            if keyword in name or keyword in desc:
                results.append({
                    'route': current_route,
                    'name': metadata.get('name'),
                    'description': metadata.get('description')
                })
            
            # Recurse into sub-routes
            sub_routes = metadata.get('routes', [])
            for sub in sub_routes:
                sub_id = sub.get('id')
                if sub_id:
                    next_route = f"{current_route.strip('/')}/{sub_id}" if current_route else sub_id
                    _search(next_route, depth + 1)

        _search(start_route, 0)
        return results

    def get_series_details(self, series_id):
        """
        Fetch details for a specific series ID using the v2 compatibility endpoint.
        """
        url = f"{self.BASE_URL}/seriesid/{series_id}"
        try:
            response = resilient_request("GET", url, session=self.session)
            response.raise_for_status()
            return response.json().get('response', {})
        except Exception as e:
            print(f"[EIA Client Warning] Failed to fetch details for EIA series ID '{series_id}': {e}")
            return {}

    def get_data_steo(self, series_ids, frequency='monthly', data_col='value', force_refresh=False):
        """
        Retrieve data from the STEO endpoint with local caching.
        """
        if isinstance(series_ids, str):
            series_ids = [series_ids]
            
        # Standardize and sort IDs for consistent cache key
        sorted_ids = sorted(list(set(series_ids)))
        cache_key = f"eia_steo_{'_'.join(sorted_ids)}_{frequency}_{data_col}"
        
        # Try local cache
        cached_df = self.cache.get(cache_key, frequency=frequency, force_refresh=force_refresh)
        if cached_df is not None:
            return cached_df

        # Fetch fresh data
        url = f"{self.BASE_URL}/steo/data/"
        params = {
            'frequency': frequency,
            'data[0]': 'value',
            'sort[0][column]': 'period',
            'sort[0][direction]': 'asc'
        }
        
        for i, sid in enumerate(series_ids):
            params[f'facets[seriesId][{i}]'] = sid
            
        data = self._get_with_pagination(url, params)
        
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['period'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # If multiple series, pivot the table
        if len(series_ids) > 1:
            df_final = df.pivot(index='date', columns='seriesId', values='value').reset_index()
        else:
            df_final = df[['date', 'value']].rename(columns={'value': data_col}).reset_index(drop=True)
            
        # Cache and return
        if not df_final.empty:
            self.cache.set(cache_key, df_final, frequency=frequency)
            
        return df_final

    def get_data(self, route, series_ids=None, frequency=None, facets=None, data_cols=None, force_refresh=False):
        """
        Generic method to fetch data from any EIA endpoint with local caching.
        """
        # Create a unique cache key based on route, series, frequency, and facets
        series_str = '_'.join(sorted(series_ids)) if isinstance(series_ids, list) else (series_ids or '')
        facets_str = str(sorted(list((facets or {}).items()))) if facets else ''
        cache_key = f"eia_route_{route.replace('/', '_')}_{series_str}_{frequency or 'default'}_{facets_str}"
        
        # Try local cache
        cache_freq = frequency or 'monthly'
        cached_df = self.cache.get(cache_key, frequency=cache_freq, force_refresh=force_refresh)
        if cached_df is not None:
            return cached_df

        # Fetch fresh data
        url = f"{self.BASE_URL}/{route.strip('/')}/data/"
        
        params = {
            'sort[0][column]': 'period',
            'sort[0][direction]': 'asc'
        }
        
        if frequency:
            params['frequency'] = frequency
            
        if not data_cols:
            data_cols = ['value']
            
        for i, col in enumerate(data_cols):
            params[f'data[{i}]'] = col
            
        final_facets = facets.copy() if facets else {}
        
        if series_ids:
            if isinstance(series_ids, str):
                series_ids = [series_ids]
            final_facets['seriesId'] = series_ids
            
        for key, values in final_facets.items():
            if not isinstance(values, list):
                values = [values]
            for i, val in enumerate(values):
                params[f'facets[{key}][{i}]'] = val
                
        data = self._get_with_pagination(url, params)
        
        if not data:
            return pd.DataFrame()
                
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['period'])
        
        for col in data_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Pivot if multiple series and single data column
        if series_ids and len(series_ids) > 1 and len(data_cols) == 1:
            df_final = df.pivot(index='date', columns='seriesId', values=data_cols[0]).reset_index()
        else:
            cols_to_keep = ['date'] + data_cols
            if 'seriesId' in df.columns and len(series_ids or []) > 1:
                cols_to_keep.append('seriesId')
            df_final = df[cols_to_keep].reset_index(drop=True)
            
        # Cache and return
        if not df_final.empty:
            self.cache.set(cache_key, df_final, frequency=cache_freq)
            
        return df_final

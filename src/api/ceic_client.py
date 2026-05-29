import os
import pandas as pd
from dotenv import load_dotenv
from ceic_api_client.pyceic import Ceic
from concurrent.futures import ThreadPoolExecutor, as_completed

class CeicSession:
    """A robust and optimized wrapper for CEIC API operations."""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.environ.get("CEIC_API_KEY")
        self.is_authenticated = False
        
    def authenticate(self):
        """Authenticate using the API key from .env."""
        if not self.api_key:
            raise ValueError("CEIC_API_KEY not found in environment variables.")
        try:
            Ceic.set_token(self.api_key)
            self.is_authenticated = True
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def search_series(self, keyword, limit=100, prioritize_wtp=True):
        """
        Search for series with enhanced metadata and prioritization.
        Uses the 'layout' information from search results to identify WTP/GEM series.
        """
        if not self.is_authenticated:
            self.authenticate()
        
        try:
            results = Ceic.search(keyword, limit=limit)
            data_obj = getattr(results, 'data', None)
            items = getattr(data_obj, 'items', []) if data_obj else []
            
            if not items:
                return []
            
            series_list = []
            for item in items:
                m = getattr(item, 'metadata', None)
                if not m:
                    continue

                # Identify World Trend Plus / GEM from 'layout'
                is_wtp = False
                db_name = "Other"
                
                layout_list = getattr(item, 'layout', [])
                if layout_list:
                    for layout in layout_list:
                        # layout is likely a LayoutInformation object
                        db_info = getattr(layout, 'database', None)
                        topic_info = getattr(layout, 'topic', None)
                        
                        db_label = ""
                        if db_info:
                            db_label = str(getattr(db_info, 'name', ''))
                        
                        topic_label = ""
                        if topic_info:
                            topic_label = str(getattr(topic_info, 'name', ''))
                        
                        if "World Trend Plus" in db_label or "Global Economic Monitor" in topic_label:
                            is_wtp = True
                            db_name = "World Trend Plus"
                            break
                        elif db_label:
                            db_name = db_label

                # Fallback to mnemonic or indicators if layout is somehow missing but it's a known GEM pattern
                mnemonic = getattr(m, 'mnemonic', '')
                if not is_wtp and mnemonic and (".CPI." in mnemonic or ".GDP." in mnemonic):
                    # GEM mnemonics often follow standardized patterns
                    is_wtp = True
                    db_name = "World Trend Plus (Inferred)"

                # Extract Source Agency
                source_name = "N/A"
                source_info = getattr(m, 'source', None)
                if source_info:
                    source_name = getattr(source_info, 'name', 'N/A')

                series_list.append({
                    'id': getattr(m, 'id', 'N/A'),
                    'name': getattr(m, 'name', 'N/A'),
                    'frequency': getattr(getattr(m, 'frequency', None), 'name', 'N/A'),
                    'unit': getattr(getattr(m, 'unit', None), 'name', 'N/A'),
                    'country': getattr(getattr(m, 'country', None), 'name', 'N/A'),
                    'source': source_name,
                    'database': db_name,
                    'is_wtp': is_wtp
                })

            # 3. Prioritization
            if prioritize_wtp:
                # Sort by is_wtp descending, then by name length (shorter names in GEM often mean more standard)
                series_list.sort(key=lambda x: (x.get('is_wtp', False), -len(str(x.get('name', '')))), reverse=True)
                
            return series_list
        except Exception as e:
            print(f"Search failed: {e}")
            return []

    def get_data(self, series_ids, with_historical_extension=True, count=10000, max_workers=10):
        """
        Fetch series data with parallel execution for speed.
        """
        if not self.is_authenticated:
            self.authenticate()
            
        if isinstance(series_ids, (str, int)):
            series_ids = [series_ids]

        # Deduplicate and filter out None/empty IDs
        series_ids = list(set([sid for sid in series_ids if sid]))

        if not series_ids:
            return pd.DataFrame()

        if not with_historical_extension:
            # Batch fetch is already fast
            try:
                res = Ceic.series(series_ids, with_historical_extension=False, count=count)
                return self._parse_response(res)
            except Exception as e:
                print(f"Batch fetch failed: {e}")
                return pd.DataFrame()

        # Parallel fetching for historical extensions
        all_dfs = []
        with ThreadPoolExecutor(max_workers=max(1, min(len(series_ids), max_workers))) as executor:
            future_to_sid = {executor.submit(self._fetch_single_series, sid, count): sid for sid in series_ids}
            for future in as_completed(future_to_sid):
                try:
                    df = future.result()
                    if not df.empty:
                        all_dfs.append(df)
                except Exception as e:
                    print(f"Parallel fetch worker failed: {e}")

        if not all_dfs:
            return pd.DataFrame()
            
        return pd.concat(all_dfs, ignore_index=True)

    def _fetch_single_series(self, sid, count):
        """Internal helper for parallel fetching."""
        try:
            res = Ceic.series([sid], with_historical_extension=True, count=count)
            return self._parse_response(res)
        except Exception as e:
            if "NON_CONTINUOUS_SERIES" in str(e):
                try:
                    res = Ceic.series([sid], with_historical_extension=False, count=count)
                    return self._parse_response(res)
                except:
                    return pd.DataFrame()
            return pd.DataFrame()

    def _parse_response(self, res):
        """Internal helper to parse CEIC response objects into a DataFrame."""
        points = []
        data_items = getattr(res, 'data', [])
        if not data_items:
            return pd.DataFrame()
            
        for item in data_items:
            m = getattr(item, 'metadata', None)
            if not m:
                continue
                
            series_name = getattr(m, 'name', 'Unknown')
            series_id = getattr(m, 'id', 'Unknown')
            source_info = getattr(m, 'source', None)
            source_name = getattr(source_info, 'name', 'Unknown') if source_info else 'Unknown'
            
            time_points = getattr(item, 'time_points', [])
            for tp in time_points:
                try:
                    points.append({
                        'date': tp.date,  # Keep as string for faster collection
                        'value': tp.value,
                        'series_id': series_id,
                        'series_name': series_name,
                        'source': source_name
                    })
                except:
                    continue
        
        if not points:
            return pd.DataFrame()
            
        df = pd.DataFrame(points)
        df['date'] = pd.to_datetime(df['date'])  # Batch conversion is MUCH faster
        return df

    def get_series_source(self, series_id) -> str:
        """Fetch the original source agency name for a series ID."""
        if not self.is_authenticated:
            self.authenticate()
        try:
            res = Ceic.series([str(series_id)], with_historical_extension=False, count=1)
            data_items = getattr(res, 'data', [])
            if data_items:
                m = getattr(data_items[0], 'metadata', None)
                if m:
                    source_info = getattr(m, 'source', None)
                    if source_info:
                        return getattr(source_info, 'name', 'Unknown')
            return 'Unknown'
        except Exception as e:
            try:
                res = Ceic.series([str(series_id)], with_historical_extension=True, count=1)
                data_items = getattr(res, 'data', [])
                if data_items:
                    m = getattr(data_items[0], 'metadata', None)
                    if m:
                        source_info = getattr(m, 'source', None)
                        if source_info:
                            return getattr(source_info, 'name', 'Unknown')
            except:
                pass
            print(f"Failed to fetch source for {series_id}: {e}")
            return 'Unknown'

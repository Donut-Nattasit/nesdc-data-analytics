import os
import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Any, Union

class APICacheManager:
    """
    Standardized SQLite Cache Manager to manage cached datasets for BOT, EIA, and PortWatch APIs.
    Adheres strictly to the Chief Economist's Freshness Mandate:
      - Monthly: 30 days validity
      - Quarterly: 90 days validity
      - Yearly: 365 days validity
      - Daily/Weekly: 7 days validity
    """
    
    DEFAULT_DB_PATH = os.path.join("database", "api_cache.db")
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or self.DEFAULT_DB_PATH
        # Ensure target directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """Initialize the SQLite database cache table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_cache (
                    cache_key TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    frequency TEXT NOT NULL,
                    last_update TEXT NOT NULL
                )
            """)
            conn.commit()
            
    def _get_validity_timedelta(self, frequency: str) -> timedelta:
        """Map frequency strings to freshness durations."""
        freq_lower = frequency.lower()
        if "quarter" in freq_lower or freq_lower == "q" or freq_lower == "qs":
            return timedelta(days=90)
        elif "month" in freq_lower or freq_lower == "m" or freq_lower == "ms":
            return timedelta(days=30)
        elif "year" in freq_lower or freq_lower == "y" or freq_lower == "a":
            return timedelta(days=365)
        elif "day" in freq_lower or "week" in freq_lower or freq_lower == "d" or freq_lower == "w":
            return timedelta(days=7)
        return timedelta(days=30)  # Default standard fallback

    def get(self, cache_key: str, frequency: str, force_refresh: bool = False) -> Optional[pd.DataFrame]:
        """
        Retrieve data from the local cache if it is fresh.
        Returns None if cache is missing, expired, or force_refresh is True.
        """
        if force_refresh:
            print(f"[Cache] Bypass: force refresh requested for key: {cache_key}")
            return None
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT payload, last_update FROM api_cache WHERE cache_key = ?", 
                    (cache_key,)
                )
                row = cursor.fetchone()
                
            if not row:
                return None
                
            payload, last_update_str = row
            last_update = datetime.strptime(last_update_str, "%Y-%m-%d %H:%M:%S")
            validity_limit = self._get_validity_timedelta(frequency)
            
            # Check if cache is still fresh
            if datetime.now() - last_update < validity_limit:
                print(f"[Cache] HIT: Fresh cached data loaded for: {cache_key} (Cached on: {last_update_str})")
                data_list = json.loads(payload)
                if not data_list:
                    return pd.DataFrame()
                df = pd.DataFrame(data_list)
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                return df
            else:
                print(f"[Cache] EXPIRED: Stale cached data found for: {cache_key} (Cached on: {last_update_str}). Requesting refresh.")
                return None
                
        except Exception as e:
            print(f"[Cache Warning] Failed to read from cache database: {e}")
            return None

    def set(self, cache_key: str, df: pd.DataFrame, frequency: str):
        """
        Store or overwrite a dataset in the local SQLite cache database.
        """
        if df.empty:
            return
            
        try:
            # Prepare data for storage: serialize dates and convert to JSON list of dicts
            df_copy = df.copy()
            if 'date' in df_copy.columns:
                if pd.api.types.is_datetime64_any_dtype(df_copy['date']):
                    df_copy['date'] = df_copy['date'].dt.strftime('%Y-%m-%d')
                else:
                    df_copy['date'] = df_copy['date'].astype(str)
                    
            payload = df_copy.to_json(orient='records')
            last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO api_cache (cache_key, payload, frequency, last_update)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(cache_key) DO UPDATE SET
                        payload=excluded.payload,
                        frequency=excluded.frequency,
                        last_update=excluded.last_update
                    """,
                    (cache_key, payload, frequency, last_update)
                )
                conn.commit()
            print(f"[Cache] SAVED: Cache registered for: {cache_key} (frequency: {frequency})")
            
            # Silent background run of the data lifecycle cleanup
            try:
                import threading
                def run_dlm_async():
                    try:
                        from src.utils.data_lifecycle import manage_data_lifecycle
                        manage_data_lifecycle()
                    except Exception:
                        pass
                threading.Thread(target=run_dlm_async, daemon=True).start()
            except Exception:
                pass
                
        except Exception as e:
            print(f"[Cache Warning] Failed to write to cache database: {e}")

    def clear(self, cache_key: Optional[str] = None):
        """Clear cache entries. Clears all if cache_key is None."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if cache_key:
                    conn.execute("DELETE FROM api_cache WHERE cache_key = ?", (cache_key,))
                    print(f"[Cache] Cleared cached key: {cache_key}")
                else:
                    conn.execute("DELETE FROM api_cache")
                    print("[Cache] Entire database cache cleared.")
                conn.commit()
        except Exception as e:
            print(f"[Cache Warning] Failed to clear cache: {e}")

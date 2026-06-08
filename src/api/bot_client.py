import os
import requests
import pandas as pd
from dotenv import load_dotenv
from src.api.network_utils import resilient_request
from src.api.cache_manager import APICacheManager

class BOTClient:
    """
    A resilient client for interacting with the Bank of Thailand (BOT) API.
    Optimized with automatic rate-limit backoff, request retries, and local caching.
    """

    BASE_URL = "https://gateway.api.bot.or.th"

    def __init__(self, token=None, db_path=None):
        """
        Initialize the client with an API token and local cache.
        """
        if token:
            self.token = token
        else:
            load_dotenv()
            self.token = os.getenv("BOT_API_TOKEN")
        
        if not self.token:
            raise ValueError("API token must be provided or set in BOT_API_TOKEN environment variable.")

        self.headers = {
            "Accept": "application/xml, application/json",
            "Authorization": self.token
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.cache = APICacheManager(db_path=db_path)

    def get_category_list(self):
        """Retrieve the list of data categories with resilient requests."""
        url = f"{self.BASE_URL}/categorylist/category_list/"
        response = resilient_request("GET", url, session=self.session)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data["result"]["category"])

    def get_series_list(self, category_code):
        """Retrieve the list of data series for a given category with resilient requests."""
        url = f"{self.BASE_URL}/categorylist/series_list/"
        params = {"category": category_code}
        response = resilient_request("GET", url, session=self.session, params=params)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data["result"]["series"])

    def _get_series_chunk(self, series_code, start_period, series_name_lang='en'):
        """Internal method to retrieve one chunk of time series data resiliently."""
        url = f"{self.BASE_URL}/observations/"
        params = {
            "series_code": series_code,
            "start_period": start_period
        }
        response = resilient_request("GET", url, session=self.session, params=params)
        response.raise_for_status()
        data = response.json()

        if not data["result"]["series"] or not data["result"]["series"][0]["observations"]:
            return pd.DataFrame()

        series_info = data["result"]["series"][0]
        df = pd.DataFrame(series_info["observations"])
        name_key = "series_name_th" if series_name_lang == 'th' else "series_name_eng"
        str_series_name = series_info.get(name_key, series_code)
        
        df = df.rename(columns={"value": str_series_name, "period_start": "date"})
        return df

    def get_data(self, series_code, start_period=None, series_name_lang='en', frequency='monthly', force_refresh=False):
        """
        Retrieve full time series data, checking the cache and handling pagination chunks.
        """
        if not start_period:
            start_period = "2000-01-01"

        # Unique cache key
        cache_key = f"bot_{series_code}_{start_period}_{series_name_lang}"
        
        # Try local cache
        cached_df = self.cache.get(cache_key, frequency=frequency, force_refresh=force_refresh)
        if cached_df is not None:
            return cached_df

        # Fetch fresh data
        start_dt = pd.to_datetime(start_period)
        today = pd.to_datetime("today")
        all_data = []
        current_start = start_dt
        chunk_years = 5 
        has_error = False

        while current_start <= today:
            try:
                df_temp = self._get_series_chunk(series_code, current_start.strftime('%Y-%m-%d'), series_name_lang)
                if not df_temp.empty:
                    all_data.append(df_temp)
            except Exception as e:
                print(f"[BOT Client Warning] Failed to fetch chunk starting {current_start.strftime('%Y-%m-%d')}: {e}")
                has_error = True
            current_start = current_start + pd.DateOffset(years=chunk_years)

        if not all_data:
            return pd.DataFrame()

        df_combined = pd.concat(all_data, ignore_index=True)
        if not df_combined.empty:
            df_combined['date'] = df_combined['date'].astype(str)
            df_combined = df_combined.drop_duplicates(subset=['date']).sort_values('date')
            df_combined['date'] = pd.to_datetime(df_combined['date'])
            
            # Save to local cache ONLY if all chunks fetched successfully
            if not has_error:
                self.cache.set(cache_key, df_combined, frequency=frequency)
            else:
                print(f"[BOT Client Warning] Bypassing cache registration for {cache_key} due to chunk fetch failures.")
            
        return df_combined

import pandas as pd
import requests
from typing import List, Dict, Optional, Any
from src.api.network_utils import resilient_request
from src.api.cache_manager import APICacheManager

class WorldBankClient:
    """
    A highly resilient, caching-enabled client for the World Bank API v2.
    Adheres strictly to the Chief Economist's Freshness Mandate and Wide Format standards.
    No API key is required for public World Bank endpoints.
    
    Base URL: https://api.worldbank.org/v2
    """
    
    BASE_URL = "https://api.worldbank.org/v2"
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the World Bank API client with persistent HTTP session and SQLite cache.
        """
        self.session = requests.Session()
        self.cache = APICacheManager(db_path=db_path)
        
    def _detect_frequency(self, frequency: str) -> str:
        """
        Standardize and return the frequency code for APICacheManager.
        """
        freq_lower = frequency.lower()
        if "year" in freq_lower or freq_lower == "a" or freq_lower == "y" or freq_lower == "annual":
            return "annual"
        elif "quarter" in freq_lower or freq_lower == "q" or freq_lower == "quarterly":
            return "quarterly"
        elif "month" in freq_lower or freq_lower == "m" or freq_lower == "monthly":
            return "monthly"
        return "annual"  # Default fallback
        
    def _standardize_date(self, date_str: str) -> str:
        """
        Standardize World Bank date strings to standard ISO dates conforming to workspace standards.
        - YYYY -> YYYY-12-31
        - YYYYQ1 -> YYYY-03-31
        - YYYYQ2 -> YYYY-06-30
        - YYYYQ3 -> YYYY-09-30
        - YYYYQ4 -> YYYY-12-31
        - YYYYM01 -> YYYY-01-31 (last day of the month)
        """
        date_str = str(date_str).strip()
        if not date_str:
            return ""
        try:
            # Check annual YYYY
            if len(date_str) == 4 and date_str.isdigit():
                return f"{date_str}-12-31"
            # Check quarterly (e.g., 2024Q1 or 2024-Q1)
            if "Q" in date_str.upper():
                clean_q = date_str.upper().replace("-", "")
                year = clean_q[:4]
                q = clean_q[-1]
                q_map = {
                    "1": "03-31",
                    "2": "06-30",
                    "3": "09-30",
                    "4": "12-31"
                }
                if q in q_map:
                    return f"{year}-{q_map[q]}"
            # Check monthly (e.g., 2024M01 or 2024-M01)
            if "M" in date_str.upper():
                clean_m = date_str.upper().replace("-", "")
                year = clean_m[:4]
                month = int(clean_m[5:])
                period = pd.Period(year=int(year), month=month, freq='M')
                return period.to_timestamp(how='end').strftime('%Y-%m-%d')
        except Exception as e:
            print(f"[World Bank Client Warning] Failed to parse date '{date_str}': {e}")
        return date_str

    def get_indicators(self, search_query: Optional[str] = None, max_records: int = 2000) -> pd.DataFrame:
        """
        Retrieve catalog of indicators from the World Bank API with pagination.
        
        Args:
            search_query (str, optional): Keyword query to filter indicators.
            max_records (int): Maximum records to retrieve (to prevent infinite loops).
            
        Returns:
            pd.DataFrame: A DataFrame containing indicator IDs, names, and source metadata.
        """
        url = f"{self.BASE_URL}/indicator"
        page = 1
        records = []
        
        print(f"[World Bank Client] Fetching catalog of indicators (up to {max_records} records)...")
        while len(records) < max_records:
            params = {
                "format": "json",
                "per_page": 1000,
                "page": page
            }
            try:
                response = resilient_request("GET", url, session=self.session, params=params)
                response.raise_for_status()
                data = response.json()
                
                # World Bank API returns metadata as the first element and observations/records as the second
                if len(data) < 2 or not isinstance(data[1], list) or not data[1]:
                    break
                    
                indicators_raw = data[1]
                for item in indicators_raw:
                    records.append({
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "source_id": item.get("source", {}).get("id"),
                        "source_value": item.get("source", {}).get("value"),
                        "sourceNote": item.get("sourceNote"),
                        "sourceOrganization": item.get("sourceOrganization")
                    })
                
                metadata = data[0]
                pages = metadata.get("pages", 1)
                if page >= pages:
                    break
                page += 1
            except Exception as e:
                print(f"[World Bank Client Error] Failed to fetch indicator catalog page {page}: {e}")
                break
                
        df = pd.DataFrame(records)
        if df.empty:
            return df
            
        if search_query:
            q = search_query.lower()
            df = df[
                df["id"].str.lower().str.contains(q, na=False) |
                df["name"].str.lower().str.contains(q, na=False) |
                df["sourceNote"].str.lower().str.contains(q, na=False)
            ]
        return df

    def get_data(
        self,
        indicator: str,
        country: str = "all",
        start_period: Optional[str] = None,
        end_period: Optional[str] = None,
        frequency: str = "annual",
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Fetch time series observations for a specific indicator and country from the World Bank API.
        Optimized with local SQLite caching.
        
        Args:
            indicator (str): The indicator ID (e.g., 'NY.GDP.MKTP.KD.ZG')
            country (str): Semicolon-separated ISO alpha-3 codes or 'all'
            start_period (str, optional): Start year/period (e.g. '2000' or '2000Q1')
            end_period (str, optional): End year/period (e.g. '2025' or '2025Q4')
            frequency (str): Code indicating series frequency ('annual', 'quarterly', 'monthly')
            force_refresh (bool): Skip cache and fetch directly from live API
            
        Returns:
            pd.DataFrame: A long DataFrame of observations: ['date', 'value', 'indicator_id', 'country_iso3', 'country_name']
        """
        freq_str = self._detect_frequency(frequency)
        cache_key = f"worldbank_{country}_{indicator}_{start_period or ''}_{end_period or ''}_{freq_str}"
        
        # Check cache
        cached_df = self.cache.get(cache_key, frequency=freq_str, force_refresh=force_refresh)
        if cached_df is not None:
            return cached_df
            
        # Build API request parameters
        url = f"{self.BASE_URL}/country/{country}/indicator/{indicator}"
        params = {
            "format": "json",
            "per_page": 1000
        }
        
        # Date parameter format standard: YYYY:YYYY or YYYYQX:YYYYQX
        if start_period and end_period:
            params["date"] = f"{start_period}:{end_period}"
        elif start_period:
            params["date"] = f"{start_period}:"
        elif end_period:
            params["date"] = f":{end_period}"
            
        records = []
        page = 1
        
        print(f"[World Bank Client] Fetching observations for indicator '{indicator}' and country '{country}'...")
        while True:
            params["page"] = page
            try:
                response = resilient_request("GET", url, session=self.session, params=params)
                
                # Check for 404 or empty indicators
                if response.status_code == 404:
                    print(f"[World Bank Client Warning] No data found (404) for query: {url}")
                    return pd.DataFrame()
                    
                response.raise_for_status()
                data = response.json()
                
                # Check structure
                if len(data) < 2 or not isinstance(data[1], list) or not data[1]:
                    break
                    
                obs_raw = data[1]
                for item in obs_raw:
                    val = item.get("value")
                    if val is not None:
                        val = float(val)
                        
                    records.append({
                        "date": self._standardize_date(item.get("date")),
                        "value": val,
                        "indicator_id": item.get("indicator", {}).get("id"),
                        "indicator_name": item.get("indicator", {}).get("value"),
                        "country_iso3": item.get("countryiso3code"),
                        "country_name": item.get("country", {}).get("value")
                    })
                    
                metadata = data[0]
                pages = metadata.get("pages", 1)
                if page >= pages:
                    break
                page += 1
            except Exception as e:
                print(f"[World Bank Client Error] Failed to fetch data page {page} from World Bank: {e}")
                break
                
        df = pd.DataFrame(records)
        
        if df.empty:
            print(f"[World Bank Client Warning] Parsed dataset is empty for query: {url}")
            return pd.DataFrame()
            
        # Cache the parsed dataset
        self.cache.set(cache_key, df, frequency=freq_str)
        return df

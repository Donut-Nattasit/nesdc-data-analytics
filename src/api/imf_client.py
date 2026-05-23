import os
import requests
import pandas as pd
from typing import List, Dict, Optional, Any
from src.api.network_utils import resilient_request
from src.api.cache_manager import APICacheManager

class IMFClient:
    """
    A highly flexible and resilient client for the IMF SDMX 3.0 API.
    Uses Azure API Management authentication (Ocp-Apim-Subscription-Key) and
    provides local SQLite caching complying with the Chief Economist's Freshness Mandate.
    
    Base URL: https://api.imf.org/external/sdmx/3.0
    """
    
    BASE_URL = "https://api.imf.org/external/sdmx/3.0"
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the IMF API client with environmental credentials and SQLite caching.
        """
        self.api_key = os.getenv("IMF_API_KEY")
        if not self.api_key:
            print("[IMF Client Warning] IMF_API_KEY environment variable is not set. API calls will fail.")
            
        self.session = requests.Session()
        self.cache = APICacheManager(db_path=db_path)
        
    def _get_headers(self) -> Dict[str, str]:
        """
        Generate HTTP headers for the IMF Azure API Management request.
        """
        headers = {
            "Accept": "application/json"
        }
        if self.api_key:
            headers["Ocp-Apim-Subscription-Key"] = self.api_key
        return headers
        
    def _detect_frequency(self, key: str, dataflow: str) -> str:
        """
        Detect frequency from key or dataflow string to determine caching validity.
        """
        key_upper = key.upper()
        dataflow_upper = dataflow.upper()
        
        # In SDMX, frequency is typically the last dimension (e.g. THA.NGDP_RPCH.A)
        # or we check if specific indicators specify it.
        if key_upper.endswith(".A") or key_upper.endswith(".Y") or ".A." in key_upper:
            return "annual"
        elif key_upper.endswith(".Q") or ".Q." in key_upper:
            return "quarterly"
        elif key_upper.endswith(".M") or ".M." in key_upper:
            return "monthly"
        elif key_upper.endswith(".D") or ".D." in key_upper:
            return "daily"
            
        # Fallbacks based on dataflow name
        if "WEO" in dataflow_upper:
            return "annual"
        elif "IFS" in dataflow_upper or "CPI" in dataflow_upper:
            return "monthly"
            
        return "monthly"  # Standard default fallback

    def get_dataflows(self) -> List[Dict[str, Any]]:
        """
        Retrieve available database schemas/dataflows from the IMF.
        """
        url = f"{self.BASE_URL}/structure/dataflow"
        headers = self._get_headers()
        
        try:
            response = resilient_request("GET", url, session=self.session, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # The structure of SDMX 3.0 lists dataflows under "data/dataflows"
            dataflows_raw = data.get("data", {}).get("dataflows", [])
            dataflows = []
            
            for df in dataflows_raw:
                name_val = df.get("name")
                if isinstance(name_val, dict):
                    name_str = name_val.get("en", df.get("id"))
                elif isinstance(name_val, str):
                    name_str = name_val
                else:
                    name_str = df.get("names", {}).get("en", df.get("id"))
                    
                dataflows.append({
                    "id": df.get("id"),
                    "agency": df.get("agencyID"),
                    "version": df.get("version"),
                    "name": name_str
                })
            return dataflows
            
        except Exception as e:
            print(f"[IMF Client Warning] Failed to fetch dataflows: {e}")
            return []

    def get_data_structure(self, dataflow: str, agency: str = "IMF.STA") -> Dict[str, Any]:
        """
        Fetch the Data Structure Definition (DSD) to discover dimensions and codes.
        """
        # Agency is typically IMF.STA for statistics department databases and IMF.RES for WEO
        actual_agency = "IMF.RES" if "WEO" in dataflow.upper() else agency
        dsd_id = f"DSD_{dataflow}"
        
        url = f"{self.BASE_URL}/structure/datastructure/{actual_agency}/{dsd_id}/~"
        headers = self._get_headers()
        
        try:
            response = resilient_request("GET", url, session=self.session, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[IMF Client Warning] Failed to fetch data structure for '{dataflow}': {e}")
            return {}

    def get_data(
        self,
        dataflow: str = "WEO",
        key: str = "THA.NGDP_RPCH.A",
        agency: str = "IMF.RES",
        version: str = "~",
        start_period: Optional[str] = None,
        end_period: Optional[str] = None,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Retrieve a dataset dynamically from any IMF dataflow.
        Uses exponential backoff retries and local SQLite caching.
        
        Args:
            dataflow (str): Dataflow ID (e.g. WEO, IFS, CPI)
            key (str): Filter key string (e.g. COUNTRY.INDICATOR.FREQUENCY)
            agency (str): Agency ID (e.g. IMF.RES for WEO, IMF.STA for statistics department)
            version (str): API version wildcard (default: ~ for latest)
            start_period (str): Start year or period (e.g., '2010')
            end_period (str): End year or period (e.g., '2025')
            force_refresh (bool): Skip local cache and force API update
            
        Returns:
            pd.DataFrame: A structured DataFrame of the timeseries, aligned with the Wide format.
        """
        # Determine frequency for cache management
        freq_str = self._detect_frequency(key, dataflow)
        
        # Build cache key
        cache_key = f"imf_{agency}_{dataflow}_{version}_{key}_{start_period or ''}_{end_period or ''}"
        cached_df = self.cache.get(cache_key, frequency=freq_str, force_refresh=force_refresh)
        
        if cached_df is not None:
            return cached_df
            
        # Construct the API request URL
        # Pattern: /data/dataflow/{agencyID}/{resourceID}/{version}/{key}
        url = f"{self.BASE_URL}/data/dataflow/{agency}/{dataflow}/{version}/{key}"
        
        params = {}
        if start_period:
            params["startPeriod"] = start_period
        if end_period:
            params["endPeriod"] = end_period
            
        headers = self._get_headers()
        
        print(f"[IMF Client] Fetching fresh data from: {url} (params: {params})")
        try:
            response = resilient_request("GET", url, session=self.session, headers=headers, params=params)
            
            if response.status_code == 404:
                print(f"[IMF Client Warning] No data found (404) for query: {url}")
                return pd.DataFrame()
            
            response.raise_for_status()
            data = response.json()
            
            # Parse the SDMX-JSON response dynamically
            df_parsed = self._parse_sdmx_json(data)
            
            if df_parsed.empty:
                print(f"[IMF Client Warning] Parsed dataset is empty for query: {url}")
                return pd.DataFrame()
                
            # Cache the parsed dataset
            self.cache.set(cache_key, df_parsed, frequency=freq_str)
            return df_parsed
            
        except Exception as e:
            print(f"[IMF Client Error] Failed to fetch data from IMF API: {e}")
            return pd.DataFrame()
            
    def get_weo_data(
        self,
        country: str,
        indicator: str,
        start_period: Optional[str] = None,
        end_period: Optional[str] = None,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        High-level wrapper optimized specifically for World Economic Outlook (WEO) datasets.
        
        Args:
            country (str): ISO alpha-3 country code (e.g. 'THA', 'USA', or multi 'THA+USA')
            indicator (str): WEO indicator code (e.g. 'NGDP_RPCH' for real GDP growth, 'PCPIPCH' for inflation)
            start_period (str): Start year (e.g. '2020')
            end_period (str): End year (e.g. '2026')
            force_refresh (bool): Skip local cache and force API update
            
        Returns:
            pd.DataFrame: A structured wide DataFrame of the WEO series.
        """
        # WEO parameters: Dataflow=WEO, Agency=IMF.RES, Frequency=A (Annual)
        key = f"{country}.{indicator}.A"
        return self.get_data(
            dataflow="WEO",
            key=key,
            agency="IMF.RES",
            start_period=start_period,
            end_period=end_period,
            force_refresh=force_refresh
        )

    def _parse_sdmx_json(self, sdmx_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Generic, high-performance parser for the SDMX-JSON 1.0/2.0 data standard.
        Dynamically extracts series and mapping dimensions into a structured DataFrame.
        """
        try:
            # Check for base structure
            data_root = sdmx_data.get("data", {})
            datasets = data_root.get("dataSets", [])
            
            if not datasets:
                return pd.DataFrame()
                
            series_dict = datasets[0].get("series", {})
            if not series_dict:
                return pd.DataFrame()
                
            # Extract metadata dimensions
            structures = data_root.get("structures", [{}])
            if not structures:
                return pd.DataFrame()
                
            structure_info = structures[0]
            series_dims = structure_info.get("dimensions", {}).get("series", [])
            obs_dims = structure_info.get("dimensions", {}).get("observation", [])
            
            if not obs_dims:
                return pd.DataFrame()
                
            obs_periods = obs_dims[0].get("values", [])
            
            records = []
            
            for series_key, series_content in series_dict.items():
                # series_key is represented as dimension indices joined by colons, e.g. "0:0:0"
                key_indices = [int(idx) for idx in series_key.split(":")]
                
                # Map series indices to dimension values
                series_metadata = {}
                for dim_idx, key_idx in enumerate(key_indices):
                    if dim_idx < len(series_dims):
                        dim_name = series_dims[dim_idx]["id"]
                        dim_value = series_dims[dim_idx]["values"][key_idx]["id"]
                        series_metadata[dim_name] = dim_value
                
                # Parse observations
                observations = series_content.get("observations", {})
                for obs_idx_str, obs_val_list in observations.items():
                    obs_idx = int(obs_idx_str)
                    
                    if obs_idx < len(obs_periods):
                        time_period = obs_periods[obs_idx].get("value")
                        
                        # Observation values are typically the first element in a list
                        val = None
                        if obs_val_list and obs_val_list[0] is not None:
                            try:
                                val = float(obs_val_list[0])
                            except ValueError:
                                val = obs_val_list[0]
                                
                        record = series_metadata.copy()
                        record["date"] = time_period
                        record["value"] = val
                        records.append(record)
                        
            if not records:
                return pd.DataFrame()
                
            df = pd.DataFrame(records)
            
            # Clean date and columns
            if "date" in df.columns:
                # If date is annual (YYYY), represent it as string or datetime
                # Let's ensure standard format
                df["date"] = df["date"].astype(str)
                
            return df
            
        except Exception as e:
            print(f"[IMF Client Error] Failed to parse SDMX-JSON payload: {e}")
            return pd.DataFrame()

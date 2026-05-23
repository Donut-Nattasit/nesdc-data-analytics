# IMF SDMX 3.0 API Reference & Usage Guide

This guide documents the integration and usage of the IMF SDMX 3.0 API Client (`src/api/imf_client.py`) within our analytical workspace.

---

## 1. Authentication & API Credentials
Authentication is enforced via the `Ocp-Apim-Subscription-Key` header using the primary subscription key registered under the IMF Developer Portal.
* **Environment Variable:** `IMF_API_KEY` (configured in `.env`).
* **Portability Protocol:** Never hardcode the key. The client automatically retrieves `os.getenv("IMF_API_KEY")`.

---

## 2. API Schema & Query Architecture
The IMF SDMX 3.0 API follows a hierarchical REST structure.
* **Base URL:** `https://api.imf.org/external/sdmx/3.0`
* **Data Retrieval Pattern:** `/data/dataflow/{agencyID}/{dataflowID}/{version}/{key}`
  * **Agency ID:** `IMF.RES` (for WEO database) or `IMF.STA` (for standard statistics databases like CPI, IFS, BOP, GFS).
  * **Dataflow ID:** The unique database code (e.g. `WEO`, `CPI`, `IFS`, `BOP`).
  * **Version:** Use `~` for the latest version.
  * **Key:** Dimensions separated by dots. Standard pattern: `COUNTRY.INDICATOR.FREQUENCY`.

### Query Syntax Rules:
1. **Multi-Selection (Union):** Join codes with `+`. Example: `THA+USA.NGDP_RPCH.A` queries both Thailand and the USA.
2. **Wildcards:** Omit a dimension or use `*` or `_T` depending on dataset guidelines. In SDMX 3.0, leaving a segment between dots empty selects all values for that dimension. Example: `.NGDP_RPCH.A` queries all countries.
3. **Time Filters:** Pass `start_period` and `end_period` to restrict date ranges.

---

## 3. Caching & Freshness Mandate
All queries are automatically cached inside the unified SQLite database (`output/data/database/api_cache.db`) using the `APICacheManager`.
* **Annual Frequency (WEO default):** Cache is valid for **365 days**.
* **Monthly Frequency (CPI default):** Cache is valid for **30 days**.
* **Quarterly Frequency (IFS/BOP default):** Cache is valid for **90 days**.
* **Bypass Cache:** Pass `force_refresh=True` to fetch fresh observations and update local cache database immediately.

---

## 4. Python Usage Examples

### A. Initializing the Client
```python
from src.api.imf_client import IMFClient

client = IMFClient()
```

### B. Fetching World Economic Outlook (WEO) Data
WEO data represents annual forecasts and historical estimates. The helper method `get_weo_data` provides rapid access:
```python
# Fetch Thailand Real GDP Growth (NGDP_RPCH) from WEO (1980 - 2028)
df = client.get_weo_data(
    country="THA",
    indicator="NGDP_RPCH",
    start_period="2010",
    end_period="2028"
)
print(df.head())
```

### C. Fetching Consumer Price Index (CPI) Data
CPI data is typically monthly. We use the generic `get_data` method and query the `CPI` dataflow hosted by `IMF.STA`:
```python
# Fetch Thailand (THA) and United States (USA) monthly CPI
df_cpi = client.get_data(
    dataflow="CPI",
    key="THA+USA.CPI._T.IX.M",  # Country.Indicator.FunctionalCat.Measure.Frequency
    agency="IMF.STA",
    start_period="2024-01",
    end_period="2026-03"
)
print(df_cpi.head())
```

### D. Fetching International Financial Statistics (IFS) Data
IFS data represents quarterly or monthly macro-financial series:
```python
# Fetch Thailand (THA) bank assets relative to GDP (quarterly)
df_ifs = client.get_data(
    dataflow="IFS",
    key="THA.FAS_FBA_XDC.Q",
    agency="IMF.STA",
    start_period="2020-Q1",
    end_period="2025-Q4"
)
print(df_ifs.head())
```

### E. Structural Schema Discovery
If you need to explore valid codes and dimensions for a new database dynamically:
```# List all available dataflows / databases
dataflows = client.get_dataflows()
for df in dataflows[:10]:
    print(f"ID: {df['id']} | Name: {df['name']}")

# Fetch and inspect the Data Structure Definition (DSD) for BOP (Balance of Payments)
dsd = client.get_data_structure("BOP")
print(dsd.keys())
```

---

## 5. Troubleshooting & Error Responses
* **401 Unauthorized:** Verify that `IMF_API_KEY` is set correctly in `.env` and matches the primary key in your IMF Developer Portal profile.
* **404 Not Found:** Check that your SDMX query key matches the exact DSD dimension structure. Query `client.get_data_structure(dataflow)` to inspect dimensions.

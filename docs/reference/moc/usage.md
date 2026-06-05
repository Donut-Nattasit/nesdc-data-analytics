# Thailand Ministry of Commerce (MOC) Trade Statistic API Reference

The Ministry of Commerce (MOC) Trade Statistic System (`https://tradereport.moc.go.th`) provides comprehensive, highly detailed public international trade statistics for Thailand. It is a critical data source for obtaining granular country-level breakdowns by Harmonized System (HS) codes and Ministry of Commerce Commodity codes.

---

## Key Features
*   **No API Key Required**: Fully open public REST exchange endpoints.
*   **Granular Classifications**: Supports both Harmonized System (HS) codes and the internal MOC Commodity structure (Com Code).
*   **Monthly Updates**: Statistics are refreshed monthly, usually after the 20th of each month.
*   **Automatic Caching**: Integrates with our `APICacheManager` following the Chief Economist's freshness mandate (30 days for monthly data, 365 days for product tables).

---

## Class Interface (`MOCClient`)

```python
from src.api.moc_client import MOCClient

client = MOCClient()
```

### 1. Product Search
Find specific HS codes or MOC commodity codes based on keyword search. Useful for finding target codes dynamically.
*   **Method**: `search_products(keyword, revision=2022, imex_type=None, order_by='hs_code', force_refresh=False)`
*   **Parameters**:
    *   `keyword` (str): Search keyword in Thai or English (e.g. `"มะพร้าว"` or `"coconut"`).
    *   `revision` (int, default `2022`): HS database revision year (e.g. 2012, 2017, 2022).
    *   `imex_type` (str, optional): filter by `'import'` or `'export'`.
    *   `order_by` (str, default `'hs_code'`): order results by `'hs_code'` or `'com_code'`.
*   **Returns**: `pd.DataFrame` containing code details, descriptions, and units.

### 2. HS Code Trade by Country (Bilateral Trade)
Extract trade value and quantity breakdowns by trading partner for a specific HS code.
*   **Methods**:
    *   `get_export_harmonize_countries(year, month, hs_code, limit=None, force_refresh=False)`
    *   `get_import_harmonize_countries(year, month, hs_code, limit=None, force_refresh=False)`
*   **Parameters**:
    *   `year` (int): Year (Gregorian, e.g. `2025`).
    *   `month` (int): Month number (1 to 12).
    *   `hs_code` (str): Harmonized System code (usually 8 or 11 digits, can accept 2, 4, 6 digits).
    *   `limit` (int, optional): Limits the number of records (e.g. top 10 partners).
*   **Returns**: `pd.DataFrame` with country-wise quantity, value in USD, and value in THB (baht), plus a standardized `date` column.

### 3. Commodity Code Trade by Country
Extract trade value and quantity breakdowns by trading partner using the internal MOC Commodity structure codes.
*   **Methods**:
    *   `get_export_commodity_countries(year, month, com_code, limit=None, force_refresh=False)`
    *   `get_import_commodity_countries(year, month, com_code, limit=None, force_refresh=False)`
*   **Parameters**:
    *   `com_code` (str): MOC Commodity structure code (usually 9 digits).
*   **Returns**: `pd.DataFrame` similar to the HS code country-breakdown.

### 4. Global Trade Country Summary
Retrieve a comprehensive summary of Thailand's international trade performance across all partner countries for a specific month.
*   **Method**: `get_summary_countries(year, month, limit=None, force_refresh=False)`
*   **Returns**: `pd.DataFrame` containing overall trade balance, export/import value, and quantities by country.

---

## Practical Code Example

```python
import pandas as pd
from src.api.moc_client import MOCClient

# 1. Initialize client
client = MOCClient()

# 2. Search for HS Codes associated with "durian"
print("Searching for durian products...")
products_df = client.search_products(keyword="durian")
print(products_df[['hs_code', 'hs_description_en', 'imex_type']].head(5))

# 3. Retrieve export country breakdown for fresh durian (HS Code: 08106000)
# Retrieve data for December 2025
hs_code = "08106000"
year = 2025
month = 12

print(f"\nRetrieving export country breakdown for HS {hs_code} on {year}-{month:02d}...")
exports_df = client.get_export_harmonize_countries(
    year=year,
    month=month,
    hs_code=hs_code,
    limit=5
)

# 4. View Top 5 Partners by USD Value
if not exports_df.empty:
    top_partners = exports_df.sort_values(by='value_usd', ascending=False)
    print(top_partners[[
        'date', 'country_name_en', 'quantity', 
        'value_usd', 'value_baht'
    ]])
else:
    print("No data returned or empty DataFrame.")
```

---

## Troubleshooting & Best Practices
*   **Slow Server Responses**: MOC servers can occasionally be slow or time out during peak government reporting periods. The client incorporates a resilient handler. For large loops across multiple months, always include a slight pause (`time.sleep(0.5)`) between requests to avoid trigger-blocking rate limits.
*   **Bypassing Cache**: If you need real-time fresher numbers (for instance, right after the monthly release date of the 20th), call endpoints with the `force_refresh=True` parameter.
*   **Wide Format Transformation**: To feed this data directly to our downstream `econometrician` or `data_scientist` agents, pivot the resulting DataFrame so that countries are represented as columns, and the `date` index represents rows.

# Fetcher API Reference (BOT & EIA)

This reference provides optimized Python patterns for the BOT and EIA clients.

## 1. BOT API (Bank of Thailand)
```python
from src.api.bot_client import BOTClient

client = BOTClient()
# Use batch search if possible
categories = client.get_category_list()
# Data retrieval handles 10-year limit automatically
df = client.get_data('RP1D', start_date='2010-01-01')
df.to_csv('output/data/bot_policy_rate.csv', index=False)
```

## 2. EIA API (U.S. Energy Information Administration)
```python
from src.api.eia_client import EIAClient

client = EIAClient()
# BATCH FETCHING (Highly Recommended)
series_ids = ['WTIPUUS', 'BREPUUS']
df = client.get_data_steo(series_ids) # Pivots automatically
df.to_csv('output/data/eia_crude_prices.csv', index=False)
```

## 3. S&P Global Connect API

```python
from src.api.sp_client import SPClient

client = SPClient()  # reads SP_USERNAME / SP_PASSWORD from .env

# Long format (raw API response)
df = client.fetch("https://api.connect.spglobal.com/shared/v1/databrowser/savedqueries/348345/Annual")

# Wide format (dates as rows, one column per Title series)
df_wide = client.fetch_wide("https://api.connect.spglobal.com/shared/v1/databrowser/savedqueries/348345/Annual")

# CLI — quick preview from terminal
# & '.\bin\python.ps1' 'src\api\sp_client.py' '<endpoint_url>'
# & '.\bin\python.ps1' 'src\api\sp_client.py' '<endpoint_url>' --wide --out output/data/projects/pmi/pmi_wide.csv
```

**Auth**: HTTP Basic — PAT as username, separate password as password.  
**Pagination**: Handled automatically by the client; pass any saved-query URL as-is.  
**Frequency path segment** (`/Annual`, `/Monthly`, `/Quarterly`): All return the same rows for most queries — use `/Annual` as default.  
**Credentials**: `SP_USERNAME` / `SP_PASSWORD` in `.env`.

## 4. General Best Practices
- **Environment**: Always load `.env` before initializing clients.
- **Pivoting**: If fetching multiple series, ensure the final CSV is in **Wide Format** (date as index, series as columns).

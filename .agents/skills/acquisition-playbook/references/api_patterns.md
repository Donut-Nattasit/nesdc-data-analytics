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

## 3. General Best Practices
- **Environment**: Always load `.env` before initializing clients.
- **Pivoting**: If fetching multiple series, ensure the final CSV is in **Wide Format** (date as index, series as columns).
- **Registration**: Always update `PROJECT_STATE.json` using `src/utils/registry.py` after a successful fetch.

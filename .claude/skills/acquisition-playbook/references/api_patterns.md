# Fetcher API Reference (BOT, EIA, S&P, SocData)

This reference provides optimized Python patterns for all data source clients.

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

## 5. NESDC SocData API (socdata.nesdc.go.th)

**Coverage**: 77 Thai provinces × 29 social indicators across 6 dimensions, annual 2015–2025.  
**Auth**: `Authorization: Bearer <SOCDATA_API_KEY>` (key in `.env`).  
**Base URL**: `https://socdata.nesdc.go.th/api/v1`  
**Note**: The site is a JavaScript SPA — WebFetch returns empty. Always call the API directly via PowerShell or Python.

### Dimensions & Indicator Codes

| Dimension | Codes |
| --- | --- |
| การศึกษา | IND05, IND06, IND08, IND34, IND35, IND36, IND37 |
| ความยากจนและการกระจายรายได้ | IND13, IND14, IND16 |
| ประชากร แรงงาน | IND09, IND10, IND11, IND33 |
| รายได้ รายจ่าย หนี้สินครัวเรือน | IND15, IND25, IND26, IND27, IND28 |
| สวัสดิการ และความมั่นคงทางสังคม | IND21, IND22, IND23, IND24 |
| สุขภาพ | IND01, IND02, IND03, IND04, IND38, IND39 |

### Endpoints

```text
GET /nesdc/public/overview_filter
  → {province: [{number_code, province_th, province_en}], indicator: [{ind_code, name, dimension}]}

GET /nesdc/public/overview?code=<province_code>
  → default: returns 2020–2025 partition (most recent 6 years)

GET /nesdc/public/overview?code=<province_code>&period[start_period]=2015&period[end_period]=2020
  → returns 2015–2020 partition (older 6 years)

GET /nesdc/public/download_file_overview?code=<province_code>&file_extension=<xlsx|csv|json>
  → file download
```

### Critical: Two-Partition Fetch Pattern

The API splits data into two 6-year partitions. **Always make both calls and merge** to get the full 2015–2025 range.

```python
import requests, os, time
import pandas as pd

API_BASE  = "https://socdata.nesdc.go.th/api/v1"
HEADERS   = {"Authorization": f"Bearer {os.environ['SOCDATA_API_KEY']}", "Accept": "application/json"}
YEAR_COLS = list(range(2015, 2026))


def get(endpoint, params=None):
    # verify=False: NESDC uses a Thai government CA not in Python's default bundle
    r = requests.get(f"{API_BASE}/{endpoint}", headers=HEADERS, params=params, timeout=30, verify=False)
    r.raise_for_status()
    j = r.json()
    assert j["result"] == "OK"
    return j["data"]


def parse_rows(data):
    out = {}
    for row in data["data_table"]:
        code = row["indicators_code"]
        out[code] = {
            "dimension": row["dimension_code"],
            "indicator": row["indicators"],
            "unit":      row["unit"],
            "values":    {int(y): (float(row[f"indicator_{y}"]) if row.get(f"indicator_{y}") not in ("", None) else None)
                          for y in data["list_year"]},
        }
    return out


def fetch_province(pcode):
    old = parse_rows(get("nesdc/public/overview",
                         {"code": pcode, "period[start_period]": 2015, "period[end_period]": 2020}))
    time.sleep(0.3)
    new = parse_rows(get("nesdc/public/overview", {"code": pcode}))
    rows = []
    for ind_code in dict.fromkeys(list(old) + list(new)):
        o, n = old.get(ind_code, {}), new.get(ind_code, {})
        row = {"ind_code": ind_code, "dimension": (o or n).get("dimension"),
               "indicator": (o or n).get("indicator"), "unit": (o or n).get("unit")}
        for y in YEAR_COLS:
            v = (o.get("values") or {}).get(y)
            row[y] = v if v is not None else (n.get("values") or {}).get(y)
        rows.append(row)
    return rows


# Get province list
filter_data = get("nesdc/public/overview_filter")
provinces   = filter_data["province"]   # [{number_code, province_th, province_en}]

# Fetch all provinces
all_rows = []
for prov in provinces:
    rows = fetch_province(prov["number_code"])
    for r in rows:
        r["province_code"] = prov["number_code"]
        r["province_th"]   = prov["province_th"]
        r["province_en"]   = prov["province_en"]
    all_rows.extend(rows)
    time.sleep(0.2)

meta = ["province_code", "province_th", "province_en", "dimension", "ind_code", "indicator", "unit"]
df = pd.DataFrame(all_rows)[meta + YEAR_COLS]
df.to_csv("output/data/projects/socdata_nesdc/all_provinces_social_indicators_2015_2025.csv",
          index=False, encoding="utf-8-sig")
```

### Known Issues

- **บึงกาฬ (A0120)**: 2020–2025 partition returns 500 (server bug) — only 2015–2020 data available.
- Some indicators only update through 2022; 2021/2022 values may be copy-forwards pending survey publication.
- Add `time.sleep(0.3)` between partition calls and `time.sleep(0.2)` between provinces to avoid rate-limiting.

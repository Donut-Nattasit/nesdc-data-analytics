---
name: acquisition-playbook
description: >
  Consolidates expert procedures for searching, refining, and retrieving economic data across multiple global and domestic databases (CEIC, BOT, EIA, IMF, World Bank, MOC, GTA, PortWatch). Use when designing data acquisition workflows, writing data-fetching scripts, or selecting appropriate economic indicators.
---

# Acquisition Playbook Skill

## Purpose
This playbook acts as the master reference for querying and consolidating time-series economic indicators into the workspace. It details database prioritizations, schema boundaries, and error-handling steps.

## Decision Tree: Database Selection
When requested to retrieve economic data, use the following logic to select the primary database:

```
                  Type of Data Required?
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
   [Global Macro]    [Thai Domestic] [Sector Specific]
         │             │             │
   ┌─────┴─────┐    ┌──┴────────┐    ├──────────────────────────┐
   ▼           ▼    ▼           ▼    ▼                          ▼
[CEIC (GEM)] [IMF/  [BOT API]  [MOC] [EIA]                      [PortWatch]
  (Default)   WB]               (Prices) (Energy/Petroleum)    (Maritime shipping)
```

1. **Global Macroeconomics**:
   - *First Priority*: **CEIC World Trend Plus (GEM)**. It contains highly standardized, long-horizon global indicators.
   - *Second Priority*: **World Bank API / IMF Developer API**. Use for specific structural development stats or global forecast updates (e.g. WEO, CPI).
2. **Thai Domestic Macroeconomics**:
   - *First Priority*: **Bank of Thailand (BOT) API**. Official source for domestic trade, monetary, and financial indices.
   - *Second Priority*: **Ministry of Commerce (MOC) API**. Prioritize for commodity retail/wholesale prices and detailed product trade data.
3. **Sector-Specific**:
   - **EIA STEO API**: Prioritize for global crude oil, petroleum products, and liquid fuels production/consumption balances.
   - **IMF PortWatch**: Use for maritime shipping transit volumes, port congestion, and shipping trade disruptions.
   - **Global Trade Atlas (GTA) SQL**: Connect to `database/core/GTA.db` for detailed historical bilateral HS-code trade records.

## Execution Protocol

### Step 1 — Scripts as Black Boxes
* Do not inspect or read full Python client implementations under `src/api/` unless debugging a connection error.
* Discover capability, query parameters, and endpoints by executing scripts with the `--help` flag from the command line:
  ```powershell
  $env:PYTHONPATH='.'; .\.venv\Scripts\python.exe src/api/bot_client.py --help
  ```

### Step 2 — Unified Retrieval Standards
* **Wide Format**: Pivot and store retrieved datasets in wide format (Index = Date, Columns = Series).
* **Storage Location**: Save all fetched time-series data to the consolidated SQLite database at `database/core/time_series.db`. Avoid writing loose `.csv` files unless the user explicitly requests a CSV export.
* **Temp Scripting**: Generate data fetcher routines inside `temp/`. Run the script, verify the database update, and run `Remove-Item` on the script immediately.

## Troubleshooting

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| `API Key Not Found` | Missing environment variable in `.env` | Ensure relevant key (e.g., `EIA_API_KEY`, `CEIC_API_KEY`) is defined in the root `.env` file. |
| `Timeout / Connection Reset` | Remote server load or proxy block | Increase timeout threshold in the client client configuration or query batch size in smaller chunks. |
| `Empty DataFrame / No Columns` | Invalid Series ID or Code format | Check target database documentation or run the search function with a broader keyword filter. |

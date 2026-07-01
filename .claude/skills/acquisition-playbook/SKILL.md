---
name: acquisition-playbook
description: >
  Consolidates expert procedures for searching, refining, and retrieving economic data across multiple global and domestic databases (CEIC, BOT, EIA, IMF, World Bank, MOC, GTA, PortWatch, NESDC SocData). Make sure to use this skill whenever the user asks to fetch economic indicators, download time-series data, or query any macro database, even if they don't explicitly say "use the acquisition playbook."
---

# Acquisition Playbook Skill

## Purpose
This playbook acts as the master reference for querying and consolidating time-series economic indicators into the workspace. It details database prioritizations, schema boundaries, and error-handling steps. 

## Decision Tree: Database Selection
When requested to retrieve economic data, use the following logic to select the primary database. **Why?** Consistent database selection ensures data continuity and avoids mixing methodologies across different sources.

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
   - **NESDC SocData API**: Use for provincial social indicators (education, poverty, labor, household debt, welfare, health) across all 77 provinces. See `references/api_patterns.md` §5.
3. **Sector-Specific**:
   - **EIA STEO API**: Prioritize for global crude oil, petroleum products, and liquid fuels production/consumption balances.
   - **IMF PortWatch**: Use for maritime shipping transit volumes, port congestion, and shipping trade disruptions.
   - **Global Trade Atlas (GTA) SQL**: Connect to `database/core/GTA.db` for detailed historical bilateral HS-code trade records.

## Execution Protocol

### Step 1 — Treat Scripts as Black Boxes
Treat the Python clients in `src/api/` as black boxes. Avoid inspecting their full implementations unless you are actively debugging a connection error. **Why?** Reading entire source files burns through your context window unnecessarily. 

Instead, discover capabilities, query parameters, and endpoints by executing scripts with the `--help` flag from the command line:
```powershell
$env:PYTHONPATH='.'; .\bin\python.ps1 src/api/bot_client.py --help
```

### Step 2 — Unified Retrieval Standards
Follow these standards to maintain database hygiene:
* **Wide Format**: Pivot and store retrieved datasets in wide format (Index = Date, Columns = Series). **Why?** It simplifies merging with existing macroeconomic datasets down the line.
* **Storage Location**: Save all fetched time-series data to the consolidated SQLite database at `database/core/time_series.db`. Avoid writing loose `.csv` files unless the user explicitly requests a CSV export.
* **Temp Scripting**: Generate data fetcher routines inside the `temp/` folder. Run the script, verify the database update, and run `Remove-Item` on the script immediately. **Why?** Leaving temporary ad-hoc fetch scripts pollutes the repository.

## Examples

**Example 1:**
*Input:* "Fetch the Thai CPI for the last 5 years."
*Action:* Use `bot_client.py --help` to learn the arguments. Write a script in `temp/fetch_cpi.py` that queries the BOT API for the CPI series, pivots to wide format, and saves to `database/core/time_series.db`. Execute the script, verify the insertion, and then delete `temp/fetch_cpi.py`.

## Troubleshooting

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| `API Key Not Found` | Missing environment variable in `.env` | Ensure relevant key (e.g., `EIA_API_KEY`, `CEIC_API_KEY`) is defined in the root `.env` file. |
| `Timeout / Connection Reset` | Remote server load or proxy block | Increase timeout threshold in the client configuration or query batch size in smaller chunks. |
| `Empty DataFrame / No Columns` | Invalid Series ID or Code format | Check target database documentation or run the search function with a broader keyword filter. |

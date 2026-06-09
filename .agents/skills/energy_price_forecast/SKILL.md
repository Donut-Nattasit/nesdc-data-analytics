---
name: energy_price_forecast
description: >
  Monthly pipeline execution for NESDC Dubai Oil Forecasting & Global Energy Analysis.
  Handles data ingestion, econometric forecasting (ARIMAX), visualization, and report 
  generation following the EIA STEO release cycle.
---

# Dubai Oil Monthly Pipeline Skill

## Purpose
This skill orchestrates the entire monthly workflow for the NESDC Dubai Oil Forecasting & Global Energy Analysis project. It should be run whenever a new month of crude oil spot/futures prices or the EIA STEO is released.

---

## 🔴 Mandatory Grill-Me Mode (Pre-Execution Gate)

> **STOP. Do NOT proceed to any pipeline step until this pre-flight interview is complete.**

Before invoking any pipeline script or agent, the Chief Economist MUST ask the user the following clarifying question and wait for an explicit answer:

### Question 1 — Forecast Horizon

**"What is your desired forecasting horizon (in months)?"**

**Dynamic Default Rule**: Before presenting options, compute the recommended default as **December of (current execution year + 1)**. For example, if the skill is invoked in any month of 2026, the suggested default is **December 2027**. Always display this computed end-month/year in the recommendation label below.

Present the following structured options:
- **(Recommended Default) Option A — Through December [current_year + 1]**: Projects to the end of next calendar year (e.g., December 2027 if run in 2026). Covers the rest of the current year plus the full following year — the standard NESDC planning horizon.
- **Option B — Short-term (6 months)**: Project through the next 2 quarters. Suitable for near-term policy briefings.
- **Option C — Long-term (through December [current_year + 2])**: Project through end of the year after next (e.g., December 2028 if run in 2026). Suitable for multi-year strategic planning. *(Note: forecast uncertainty widens significantly beyond 18 months.)*
- **Option D — Custom**: User specifies an exact target end month and year.

> ⚠️ **Do NOT silently assume a horizon.** Pipeline execution is BLOCKED until the user explicitly confirms or accepts the recommended default.

Once the user confirms the horizon:
1. Compute the exact number of months from the **current month** to the confirmed end month/year (inclusive) and echo back: *"Confirmed: Forecast horizon set to **N months** through **[Month Year]**."*
2. Pass the horizon value to all relevant pipeline scripts as appropriate (update `orchestrator.py` arguments or relevant script config if required).
3. Only then proceed to **Step 1** of the Monthly Update Workflow below.

---

## 📅 Monthly Update Workflow

Whenever a new month of crude oil spot/futures prices or EIA STEO statistics is released, follow this 3-step workflow to update the entire workspace:

### Step 1: Verify and Update Local Input Files
Before running the pipeline, ensure the user has updated the local Excel file. Ask the user to confirm they have updated:
- `input/pipeline/dubai_oil/dubai_price.xlsx`
  - **`spot` sheet**: Add the new daily observations for the latest month (specifically update the date column, the `GIOS0097 Index` (Dubai Bloomberg spot), and the `PGCRDUBA Index` (Platts Dubai spot)).
  - **`future` sheet**: Add the daily traded futures curve contracts (columns `DBL1 Comdty` through `DBL24 Comdty`) priced as of the latest day/month.
  - Save and close the Excel file before proceeding.

### Step 2: Trigger the Automated Pipeline
Execute the complete pipeline script from the root workspace directory using PowerShell:

```powershell
cd src\pipeline\energy_price_forecast
.\run_pipeline.ps1
```

*Alternative (standard CMD/PowerShell from workspace root):*
```powershell
$env:PYTHONPATH='.'; .\.venv\Scripts\python.exe src/pipeline/energy_price_forecast/orchestrator.py
```

### Step 3: Verify and Review Outputs
Upon successful completion, the pipeline automatically:
1. Ingests the new Excel data and fetches fresh international indicators from the **U.S. EIA STEO API** and **CEIC Global Database API**.
2. Performs wide-format merges, weekly-to-monthly resampling, and unit transformations.
3. Automatically estimates the **ARIMAX levels model**, executes residual ADF unit root stationarity audits, and outputs forecast projections through December 2027.
4. Regenerates all professional visual charts with standard fixed sizes and center-anchored titles.
5. Re-compiles the final structured markdown **Special Economic Report**, updating all embedded spreadsheets, figures, and model specifications.
6. Updates the central workspace manifest registry (`PROJECT_STATE.json`) for full auditability.

Review the updated report and charts:
*   **Special Economic Report**: `report/energy_price_forecast/energy_price_forecast.md`
*   **Global Prices Chart**: `output/chart/energy_price_forecast/global_oil_prices_comparison.png`
*   **Situation Chart**: `output/chart/energy_price_forecast/dubai_oil_situation.png`
*   **Forecast Chart**: `output/chart/energy_price_forecast/dubai_oil_forecast_comparison.png`

---

## 🛠️ Centralized Pipeline Components

For advanced customization or debugging, the pipeline runs the following 6 scripts in sequential order:

| Step | Phase | Script File | Key Responsibilities | Primary Output |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Ingest** | `prepare_data.py` | Ingests local Excel sheets; queries EIA API for Brent/WTI spot and global balance actuals; merges into wide format. | `output/data/energy_price_forecast/dubai_oil_master.csv` |
| **2** | **Model** | `predict_model.py` | Estimates two-stage Engle-Granger Error Correction Model (ECM) and exports forecasted levels. | `output/data/energy_price_forecast/dubai_oil_forecast_production.csv` |
| **3** | **Visualize**| `viz_global_prices.py` | Renders monthly benchmark spot pricing (Brent, WTI, Dubai) marked with key historical geopolitical milestones. | `output/chart/energy_price_forecast/global_oil_prices_comparison.png` |
| **4** | **Visualize**| `viz_dubai_situation.py` | Renders current year daily spot fluctuations, monthly actual averages, and expanding cumulative YTD curve. | `output/chart/energy_price_forecast/dubai_oil_situation.png` |
| **5** | **Visualize**| `viz_dubai_forecast.py` | Renders historical actual spot path, model projections path, and the raw baseline futures curve through Dec 2027. | `output/chart/energy_price_forecast/dubai_oil_forecast_comparison.png` |
| **6** | **Report** | `generate_report.py` | Synthesizes physical actuals spreads, resampled forecast tables, and quarterly spreads; embeds all figures. | `report/energy_price_forecast/energy_price_forecast.md` |

---

## 🔒 Freshness & Cache Policies

To maximize performance and prevent redundant API queries, our network layer operates on a **Cache-First** basis using SQLite caches.
*   **Pipeline database**: Stored at `database/energy_price_forecast/energy_price_forecast.db`.
*   **Volatile Series (Daily Spot)**: Automatically bypasses local caches if refreshed or specified by user overrides to pull fresh Bloomberg/Platts endpoints.
*   **Macro Series (EIA STEO / CEIC)**: If a dataset exists but its "Last Update" is older than its frequency (e.g., >1 month for Monthly EIA data, >1 week for CEIC weekly series), the client will automatically trigger a refresh query to the API, pulling the most recent observations.
*   **Manual Override**: To force-bypass all cached elements, pass the `force_refresh=True` parameter to client data queries in the scripts.

> ⚠️ **EIA STEO — Mandatory Force-Refresh Rule (Permanent)**
>
> The `APICacheManager` treats monthly data as fresh for **30 days**. However, the EIA STEO is published once per month (typically around the 10th). If the pipeline is run mid-month after a new STEO release, the cache may still appear "fresh" from the prior month's fetch and serve **stale (previous month's) data**.
>
> To prevent this, **both EIA STEO calls in `prepare_data.py` are hardcoded with `force_refresh=True`**. This ensures the Dubai oil pipeline always retrieves the current month's STEO release, regardless of cache state. Do **not** change this back to `force_refresh=False`.

---

## Troubleshooting

| Issue | Resolution |
|-------|-----------|
| Pipeline fails to find Python | Ensure the virtual environment is correctly set up at `.\.venv\` in the project root. |
| Stale EIA data in output | Confirm that `prepare_data.py` still has `force_refresh=True` enabled for its EIA STEO queries. |
| Excel Read Errors | Ensure the user has closed the `dubai_price.xlsx` file before running the script. |

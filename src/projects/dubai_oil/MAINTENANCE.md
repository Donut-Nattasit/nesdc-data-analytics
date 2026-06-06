# Workspace Maintenance & Monthly Pipeline Workflow Guide

Welcome! This guide outlines the standard operating procedure for updating the **NESDC Dubai Oil Forecasting & Global Energy Analysis** workspace on a recurring monthly basis. 

To ensure statistical rigor, data freshness, and policy-relevant report consistency, the entire pipeline has been fully automated through a centralized **Master Orchestrator**. 

---

## 📅 Monthly Update Workflow

Whenever a new month of crude oil spot/futures prices or EIA STEO statistics is released, follow this 3-step workflow to update the entire workspace:

### Step 1: Update Local Input Files
1. Open `input/projects/dubai_oil/dubai_price.xlsx` in Excel.
2. In the **`spot`** sheet: Add the new daily observations for the latest month (specifically update the date column, the `GIOS0097 Index` (Dubai Bloomberg spot), and the `PGCRDUBA Index` (Platts Dubai spot)).
3. In the **`future`** sheet: Add the daily traded futures curve contracts (columns `DBL1 Comdty` through `DBL24 Comdty`) priced as of the latest day/month.
4. Save and close the Excel file.

### Step 2: Trigger the Automated Pipeline
Open your PowerShell console at the project root directory and run the following single command:

```powershell
cd src\projects\dubai_oil
.\run_pipeline.ps1
```

*Alternative (standard cmd/bash):*
```bash
powershell -Command "Set-Item env:PYTHONPATH '.'; .\.venv\Scripts\python.exe orchestrator.py"
```

### Step 3: Verify and Review Outputs
Upon successful completion, the pipeline automatically:
1. Feeds the new Excel data and fetches fresh international indicators from the **U.S. EIA STEO API** and **CEIC Global Database API**.
2. Performs wide-format merges, weekly-to-monthly resampling, and unit transformations.
3. Automatically estimates the **ARIMAX levels model**, executes the residual ADF unit root stationarity audits, and outputs forecast projections through December 2027.
4. Regenerates all professional visual charts with standard fixed sizes and center-anchored titles.
5. Re-compiles the final structured markdown **Special Economic Report**, updating all embedded spreadsheets, figures, and model specifications.
6. Updates the central workspace manifest registry (`PROJECT_STATE.json`) for full auditability.

---

## 🛠️ Centralized Pipeline Components

For advanced customization or debugging, the pipeline runs the following 6 scripts in sequential order:

| Step | Phase | Script File | Key Responsibilities | Primary Output |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Ingest** | `prepare_data.py` | Ingests local Excel sheets; queries EIA API for Brent/WTI spot and global balance actuals; merges into wide format. | `output/data/dubai_oil_master.csv` |
| **2** | **Model** | `predict_model.py` | Estimates two-stage Engle-Granger Error Correction Model (ECM) and exports forecasted levels. | `output/data/dubai_oil_forecast_production.csv` |
| **3** | **Visualize**| `viz_global_prices.py` | Renders monthly benchmark spot pricing (Brent, WTI, Dubai) marked with key historical geopolitical milestones. | `output/chart/global_oil_prices_comparison.png` |
| **4** | **Visualize**| `viz_dubai_situation.py` | Renders current year daily spot fluctuations, monthly actual averages, and expanding cumulative YTD curve. | `output/chart/dubai_oil_situation.png` |
| **5** | **Visualize**| `viz_dubai_forecast.py` | Renders historical actual spot path, model projections path, and the raw baseline futures curve through Dec 2027. | `output/chart/dubai_oil_forecast_comparison.png` |
| **6** | **Report** | `generate_report.py` | Synthesizes physical actuals spreads, resampled forecast tables, and quarterly spreads; embeds all figures. | `report/dubai_oil/01_dubai_price.md` |

---

## 🔒 Freshness & Cache Policies

To maximize performance and prevent redundant API queries, our network layer operates on a **Cache-First** basis using SQLite caches (`database/api_cache.db`).
*   **Volatile Series (Daily Spot)**: Automatically bypasses local caches if refreshed or specified by user overrides to pull fresh Bloomberg/Platts endpoints.
*   **Macro Series (EIA STEO / CEIC)**: If a dataset exists but its "Last Update" is older than its frequency (e.g., >1 month for Monthly EIA data, >1 week for CEIC weekly series), the client will automatically trigger a refresh query to the API, pulling the most recent observations.
*   **Manual Override**: To force-bypass all cached elements, pass the `force_refresh=True` parameter to client data queries in the scripts.

> ⚠️ **EIA STEO — Mandatory Force-Refresh Rule (Permanent)**
>
> The `APICacheManager` treats monthly data as fresh for **30 days**. However, the EIA STEO is published once per month (typically around the 10th). If the pipeline is run mid-month after a new STEO release, the cache may still appear "fresh" from the prior month's fetch and serve **stale (previous month's) data**.
>
> To prevent this, **both EIA STEO calls in `prepare_data.py` are hardcoded with `force_refresh=True`**. This ensures the Dubai oil pipeline always retrieves the current month's STEO release, regardless of cache state. Do **not** change this back to `force_refresh=False`.

*Guide compiled and registered in workspace records.*

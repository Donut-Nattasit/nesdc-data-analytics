---
name: dubai-oil-pipeline
description: >
  Monthly pipeline execution for NESDC Dubai Oil Forecasting & Global Energy Analysis.
  Handles data ingestion, econometric forecasting (ARIMAX), visualization, and report 
  generation following the EIA STEO release cycle.
---

# Dubai Oil Monthly Pipeline Skill

## Purpose
This skill orchestrates the entire monthly workflow for the NESDC Dubai Oil Forecasting & Global Energy Analysis project. It should be run whenever a new month of crude oil spot/futures prices or the EIA STEO is released.

## Execution Protocol

### Step 1 — Verify Local Input Files
Before running the pipeline, ensure the user has updated the local Excel file. Ask the user to confirm they have updated:
- `input/pipeline/dubai_oil/dubai_price.xlsx`
  - **`spot` sheet**: Ensure latest daily observations for the month are added.
  - **`future` sheet**: Ensure daily traded futures curve contracts are priced as of the latest day/month.

### Step 2 — Run the Orchestrator
Execute the complete pipeline script from the root workspace directory using the standard runner:

```powershell
cd src\pipeline\dubai_oil
.\run_pipeline.ps1
```

*Alternative if ps1 execution fails:*
```powershell
powershell -Command "Set-Item env:PYTHONPATH '.'; .\.venv\Scripts\python.exe src\pipeline\dubai_oil\orchestrator.py"
```

### Step 3 — Verify Output Artifacts
The pipeline automatically produces the following key artifacts. You should review them for correctness:
- **Forecast Data**: `output/data/dubai_oil_forecast_production.csv`
- **Global Prices Chart**: `output/chart/global_oil_prices_comparison.png`
- **Situation Chart**: `output/chart/dubai_oil_situation.png`
- **Forecast Chart**: `output/chart/dubai_oil_forecast_comparison.png`
- **Special Economic Report**: `report/dubai_oil/01_dubai_price.md`

Verify that the markdown report contains updated tables and that the visual charts reflect the latest month's data.

## Data Freshness & Cache Overrides
The pipeline uses a SQLite cache-first network layer. 
> ⚠️ **CRITICAL: EIA STEO Mandatory Force-Refresh**
> The EIA STEO is published mid-month. To ensure the current month's STEO is fetched rather than a stale cache from the prior month, `force_refresh=True` is **hardcoded** in `prepare_data.py` for EIA API calls. **Do not modify this rule.**

## Pipeline Components Reference
For debugging or component execution, these are the internal scripts executed by the orchestrator in sequence:
1. `prepare_data.py`: Ingests local Excel and remote API data, merges into wide format.
2. `predict_model.py`: Estimates ECM/ARIMAX and generates forecasts.
3. `viz_global_prices.py`: Renders monthly benchmark spot pricing.
4. `viz_dubai_situation.py`: Renders current year daily spot fluctuations.
5. `viz_dubai_forecast.py`: Renders forecast paths and futures curves.
6. `generate_report.py`: Synthesizes final markdown report.

## Troubleshooting
| Issue | Resolution |
|-------|-----------|
| Pipeline fails to find Python | Ensure the virtual environment is correctly set up at `.\.venv\` in the project root. |
| Stale EIA data in output | Confirm that `prepare_data.py` still has `force_refresh=True` enabled for its EIA STEO queries. |
| Excel Read Errors | Ensure the user has closed the `dubai_price.xlsx` file before running the script. |

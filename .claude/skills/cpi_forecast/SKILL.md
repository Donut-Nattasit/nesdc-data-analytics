---
name: cpi-forecast
description: >
  Executes the monthly NESDC Consumer Price Index (CPI) forecasting pipeline. Ingests CEIC series, reverse-engineers indices/weights, fits ARIMA/ARIMAX models, aggregates Headline/Core/Non-Core indices, and compiles the monthly briefing report.
---

# Consumer Price Index (CPI) Monthly Pipeline Skill

## Purpose
This skill orchestrates the monthly workflow for the NESDC CPI Forecasting project. It automatically pulls actual CPI indices and weights from the CEIC API, reverse-engineers specific indices (like separating utilities and motor fuel components), trains ARIMA/ARIMAX models, re-aggregates the aggregates (Core, Non-Core Raw Food, Non-Core Energy, Headline), and compiles a comprehensive situation report.

## Decision Tree: Execution and Freshness Flow
Follow this tree to determine execution steps and parameters:

```
                            Determine Forecast Horizon
                     (December of [Current Year + 1] e.g. Dec 2027)
                                         │
                                         ▼
                            Check CEIC Database Cache
                       (prepare_data.py table cpi_raw_long)
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼ (Cache has current month data)            ▼ (New month published)
             Load Cached Raw data                         Call CEIC API for new series
                   │                                           │
                   └─────────────────────┬─────────────────────┘
                                         ▼
                             Run Model & Aggregations
                            (ARIMA / ARIMAX auto-fit)
                                         │
                                         ▼
                             Generate Visuals & Report
```

## Execution Protocol

### Step 1 — Verify Exogenous Dubai Oil Price Forecasts
* The CPI forecasting pipeline uses the forecasted Dubai Crude spot price as an exogenous regressor for the `Transport & Communication: Motor Fuel` component index.
* Ensure the Dubai Crude forecast file `output/data/energy_price_forecast/dubai_oil_forecast_production.csv` exists and is updated. If not, run the `energy-price-forecast` skill first.

### Step 2 — Run the Pipeline Orchestrator
* Execute the orchestrator script using the PowerShell environment template:
  ```powershell
  $env:PYTHONPATH='.'; $env:PYTHONUTF8='1'; .\.venv\Scripts\python.exe src/pipeline/cpi_forecast/orchestrator.py
  ```
* The script will execute all phases in sequence:
  1. `prepare_data.py`: Fetches missing CPI actuals from CEIC API, reverse-engineers weights/indices, and saves `cpi_historical_master.csv`.
  2. `predict_model.py`: Fits ARIMA (15 components) and ARIMAX (Motor Fuel) models, forecasts weights, aggregates composite CPIs, and resamples to Quarterly and Annual averages.
  3. `generate_charts.py`: Generates the primary composite and component line charts.
  4. `generate_report.py`: Builds Figure 10 to Figure 13 (including the Figure 11 component weight area chart) and compiles the Markdown report `report/cpi_forecast/cpi_forecast.md`.

### Step 3 — Post-Flight Verification
* Check that Figure 11 (`chart_appendix_weight_area_component.png`) starts at year 2018 to avoid pre-2018 weight series gaps.

## Troubleshooting

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| `[FAIL] Exogenous Dubai Oil forecast not found` | The `energy_price_forecast` pipeline has not been executed | Run the Dubai Oil forecasting pipeline first to generate `dubai_oil_forecast_production.csv`. |
| `CEIC API Rate Limit / Connection timeout` | Temporary API server issues or rate limits | The preparation script automatically retries fetching with exponential backoff up to 5 times. If it still fails, check network connectivity. |
| `Figure 11 has blank columns/areas` | Slicing start date is set prior to 2018 | Confirm that line 553 in `generate_report.py` is slicing index starting at `"2018-01-01":` to filter out unpopulated historical weight rows. |

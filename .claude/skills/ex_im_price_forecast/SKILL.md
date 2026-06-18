---
name: ex-im-price-forecast
description: >
  Executes the monthly NESDC Export & Import Price analysis and forecasting pipeline. Use to ingest BOT/CEIC trade indices, fit univariate and exogenous cointegration models, aggregate indices, and compile the Special Economic Brief.
---

# Export & Import Price Monthly Pipeline Skill

## Purpose
This skill manages the monthly updates, forecasting, and reporting pipeline for Thailand's Export and Import Price Indices. It relies on Bank of Thailand (BOT) and CEIC endpoints, fits univariate and exogenous models, aggregates components, and compiles a comprehensive brief.

## Decision Tree: Horizon Validation & Dependencies
Before running the pipeline, execute the following validations:

```
                          Calculate target horizon length
                                         │
                  ┌──────────────────────┴──────────────────────┐
                  ▼                                             ▼
        Check if Dubai forecast exists                 Check forecast horizon length
  (dubai_oil_forecast_production.csv)               (Does it cover target horizon?)
                  │                                             │
          ┌───────┴───────┐                             ┌───────┴───────┐
          ▼ (Yes)         ▼ (No)                        ▼ (Yes)         ▼ (No)
     [Proceed]      [ABORT: Run Dubai             [Proceed to    [ABORT: Re-run Dubai
                     pipeline first]               pipeline]      oil with longer horizon]
```

## Execution Protocol

### Step 1 — Dependency Pre-Check
* Verify that `output/data/energy_price_forecast/dubai_oil_forecast_production.csv` exists and covers the target forecast horizon.
* Set the forecast horizon parameter (default matches the Dubai Oil planning horizon).

### Step 2 — Run the Pipeline Orchestrator
* Trigger the pipeline runner script from the root workspace directory using the standard environment template:
  ```powershell
  $env:PYTHONPATH='.'; .\.venv\Scripts\python.exe src/pipeline/ex_im_price_forecast/orchestrator.py
  ```
* The pipeline runs components sequentially (Prepare -> Plot -> StatsForecast -> Exogenous -> Aggregate -> Resample & Report) and outputs data files to `output/data/ex_im_price_forecast/` and the report to `report/ex_im_price_forecast/`.

## Troubleshooting

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| `FileNotFoundError: Dubai Oil Forecast` | The Dubai oil forecasting pipeline was not run | Run the `energy_price_forecast` pipeline first. |
| `API Fetch Failure (BOT/CEIC)` | Connection or proxy blockage | Verify internet access and client endpoints. Try setting `force_refresh=True` to bypass cache if it's corrupted. |
| `Database Locked / DB Busy` | Another query or database tool is holding a lock on the SQLite file | Close other database connections to `database/ex_im_price_forecast/ex_im_price_forecast.db`. |
| `Splicing index calibration error` | Historical base indices do not align with newer series | Ensure base years match and verify data structure in `prepare_data.py`. |

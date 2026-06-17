---
name: energy-price-forecast
description: >
  Executes the monthly NESDC Dubai Crude Oil forecasting pipeline. Use to ingest daily spot/futures data, run ARIMAX levels models, render comparison charts, and generate the Special Economic Report.
---

# Dubai Oil Monthly Pipeline Skill

## Purpose
This skill orchestrates the entire monthly workflow for the NESDC Dubai Oil Forecasting & Global Energy Analysis project. It merges local excel updates, queries global benchmarks, fits ARIMAX levels models, and outputs a formal situation brief.

## Decision Tree: Horizon Selection & Cache Flow
When executing the pipeline, follow this path to configure parameters:

```
                          Calculate Recommended Horizon
               (December of [Current Execution Year + 1] e.g. Dec 2027)
                                         │
                  ┌──────────────────────┴──────────────────────┐
                  ▼ (User Accepts Default)                      ▼ (User Overrides)
           Option A: Dec [Year + 1]                      Option B/C/D: 6m, 2yr, custom
                  │                                             │
                  └──────────────────────┬──────────────────────┘
                                         ▼
                             Check Excel Input Freshness
                        (prepare_data.py Spot & Futures curve)
                                         │
                  ┌──────────────────────┴──────────────────────┐
                  ▼ (Yes)                                       ▼ (No)
            [Run Orchestrator]                            [Prompt User to Update]
```

## Execution Protocol

### Step 1 — Pre-Flight Horizon Check
* Before executing, compute the default horizon month: **December of (current execution year + 1)**.
* Ask the user to confirm this horizon before triggering the pipeline.

### Step 2 — Verify Input Files
* Ensure the local excel workbook `input/pipeline/dubai_oil/dubai_price.xlsx` has been populated with the latest daily spot and futures contracts.

### Step 3 — Run the Pipeline Orchestrator
* Execute the orchestrator script using the Python template:
  ```powershell
  $env:PYTHONPATH='.'; .\.venv\Scripts\python.exe src/pipeline/energy_price_forecast/orchestrator.py
  ```
* The pipeline will sequentially run the 6 component scripts (Prepare -> Model -> Viz -> Report) and save the outputs to `output/data/energy_price_forecast/` and `report/energy_price_forecast/`.

### Step 4 — Register Artifacts
* Log the models, datasets, and charts to `PROJECT_STATE.json` by running the registry script.

## Troubleshooting

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| `PermissionError: Excel file open` | The user has `dubai_price.xlsx` open in another application | Ask the user to save and close Excel, then re-run the pipeline. |
| `Stale EIA STEO data` | Local SQLite cache served old month data | Ensure that `prepare_data.py` passes `force_refresh=True` to the EIA STEO API fetcher. |
| `ConvergenceWarning / Singular Matrix` | Excess lags or multicollinear exogenous regressors | Simplify the ARIMAX configuration in `predict_model.py`. |

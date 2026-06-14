---
name: energy_forecast
description: Monthly pipeline execution for Dubai Crude Oil forecasting and energy situation report.
---

# Dubai Crude Oil Forecasting Workflow

## Objective
Run the monthly forecasting and situation analysis pipeline for Dubai Crude Oil. This updates historical spot and futures pricing data, integrates the latest EIA Short-Term Energy Outlook (STEO) balance variables, estimates Engle-Granger Error Correction Models (ECM), renders analytical visualizations, and synthesizes the Special Economic Report.

## Phase 1: Data Preparation & EIA Ingestion
**Agent**: `@data_fetcher`

1. **Verify Local Inputs**: Ensure the spreadsheet at [dubai_price.xlsx](file:///c:/Users/natta/OneDrive%20-%20nesdc.go.th/NESDC/MyAI/data-analysis/input/pipeline/dubai_oil/dubai_price.xlsx) is updated with the latest daily spot and futures records.
2. **Ingest EIA STEO Data**: Retrieve Brent and WTI crude oil prices (`WTIPUUS`, `BREPUUS`) along with World Petroleum Supply/Demand/Inventory metrics (`PAPR_WORLD`, `PATC_WORLD`, `T3_STCHANGE_WORLD`) directly using the EIA API.
3. **Resample and Merge**: Compute monthly averages (Month-Start `'MS'`) for daily spot/futures, merge with EIA STEO metrics, and export the unified master dataset to [dubai_oil_master.csv](file:///c:/Users/natta/OneDrive%20-%20nesdc.go.th/NESDC/MyAI/data-analysis/output/data/energy_price_forecast/dubai_oil_master.csv).

## Phase 2: Econometric Modeling & Forecasting
**Agent**: `@econometrician`

1. **Model Calibration**: Execute the Engle-Granger Cointegration and Error Correction Model (ECM) suite to verify long-term equilibrium relationships.
2. **Horizon Selection**: Determine the target prediction horizon (typically December of the subsequent year, e.g., Dec 2027) based on current execution date.
3. **Generate Projections**: Forecast spot prices using exogenous futures curves and global demand models. Save predictions to [dubai_oil_forecast_production.csv](file:///c:/Users/natta/OneDrive%20-%20nesdc.go.th/NESDC/MyAI/data-analysis/output/data/energy_price_forecast/dubai_oil_forecast_production.csv).

## Phase 3: Visual Assets Generation
**Agent**: `@viz_expert`

Create three key visualizations to support report insights, applying localized typography standards if requested:
1. **Global Benchmarks**: Plot Brent vs. WTI vs. Dubai spot trends.
2. **Dubai Spot Situation**: Plot raw historical spot movements and recent indicators.
3. **Dubai Forecast Comparison**: Plot projected paths alongside futures bands.
   * *Output location*: `output/chart/energy_price_forecast/`

## Phase 3.5: Downstream CPI & Shock Projections
**Agents**: `@econometrician` & `@data_transformer`

1. **CPI Baseline Forecast**: Run the CPI forecasting pipeline using the newly updated `dubai_oil_forecast_production.csv` as an exogenous input. This updates `cpi_forecast_monthly.csv`.
2. **Prepared Food Shock Simulation**: Run the geopolitical prepared food shock scenario simulation using the updated baseline CPI dataset to produce the comparison dataset and charts:
   * *Output CSV*: `output/data/prepared_food_shock/prepared_food_shock_comparison.csv`
   * *Output Charts*: `output/chart/prepared_food_shock/`
3. **Prepared Food Scenario Brief**: Compile the scenario report `report/prepared_food_shock/prepared_food_shock.md`.

## Phase 4: Report Synthesis & Verification
**Agent**: `@report_writer`

1. **Compile Special Economic Report**: Merge econometric findings, visual charts, energy market qualitative insights, and the downstream Prepared Food CPI Shock Scenario results (comparison table and aggregates chart) into the formal Markdown document at [energy_price_forecast.md](file:///c:/Users/natta/OneDrive%20-%20nesdc.go.th/NESDC/MyAI/data-analysis/report/energy_price_forecast/energy_price_forecast.md).
2. **Verify Layout & Captions**: Invoke the `@viz_inspector` to ensure all charts are embedded with appropriate figure and table numbers, and no path links are broken.
3. **Update Registry**: Log the new data, model outputs, and reports to `PROJECT_STATE.json` using the local registry utility.

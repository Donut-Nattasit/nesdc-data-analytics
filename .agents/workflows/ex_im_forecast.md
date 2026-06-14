---
name: ex_im_forecast
description: Monthly pipeline execution for Export and Import price forecasting and trade terms analysis.
---

# Export & Import Price Forecasting Workflow

## Objective
Run the monthly forecasting and trade terms analysis pipeline for Thailand's Export and Import Prices. This updates trade index data, estimates univariate baseline forecasts, performs cointegration modeling with Dubai Crude Oil as an exogenous driver, aggregates composite trade terms indices, and outputs a situation brief.

## Phase 1: Data Preparation & Ingestion
**Agent**: `@data_fetcher`

1. **BOT API Ingestion**: Download Bank of Thailand (BOT) trade indices (export value, import value, export volume, import volume, export price, import price) at standard classification levels.
2. **Harmonize Frequencies**: Resample daily datasets to monthly intervals, saving indices in Wide Format inside the cache database.
   * *Output location*: `database/ex_im_price_forecast/ex_im_price_forecast.db`

## Phase 2: Historical Asset Analysis
**Agent**: `@viz_expert`

1. **Calculate Contributions**: Compute rolling historical contributions for export and import categories.
2. **Chart Ingestion**: Render charts illustrating recent trends in the trade balance and export-import price indices.
   * *Output location*: `output/chart/ex_im_price_forecast/`

## Phase 3: Baseline Forecasting
**Agent**: `@data_scientist`

1. **StatsForecast Modeling**: Run univariate time series baseline models (AutoARIMA, AutoETS, Theta) on component indices.
2. **Evaluate Baseline**: Output model selection diagnostics and validation criteria metrics.

## Phase 4: Cointegration & Exogenous Model Calibration
**Agent**: `@econometrician`

1. **Exogenous Integration**: Extract Brent/Dubai oil forecasts from the [energy_price_forecast](file:///c:/Users/natta/OneDrive%20-%20nesdc.go.th/NESDC/MyAI/data-analysis/output/data/energy_price_forecast/dubai_oil_forecast_production.csv) pipeline.
2. **ARDL/ARIMAX Fitting**: Calibrate and estimate Auto-Regressive Distributed Lag (ARDL) models linking fuel imports and petroleum product exports to world crude prices.

## Phase 5: Weight Aggregation & Splicing
**Agent**: `@data_transformer`

1. **Compute Composites**: Combine forecast series components using HS-classification trade weights to construct Headline Export and Import Price Indices.
2. **Resampling**: Aggregate monthly predictions into quarterly and annual datasets using strict Quarter-End (`QE`) mean averaging.
   * *Output location*: `output/data/ex_im_price_forecast/`

## Phase 6: Report Generation & Registry Manifest
**Agent**: `@report_writer`

1. **Report Compilation**: Write the situation report containing analysis, figures, and data source attributions to [ex_im_price_forecast.md](file:///c:/Users/natta/OneDrive%20-%20nesdc.go.th/NESDC/MyAI/data-analysis/report/ex_im_price_forecast/ex_im_price_forecast.md).
2. **Verify Figures**: Let the `@viz_inspector` verify sequential figure/table captioning and image links.
3. **Register Manifest**: Execute the registry update script to log new datasets, models, and reports in `PROJECT_STATE.json`.

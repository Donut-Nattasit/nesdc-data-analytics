---
name: cpi_prediction
description: Monthly pipeline execution for Thailand's CPI prediction report.
---

# CPI Prediction Workflow

## Objective
Predict Thailand's Consumer Price Index (CPI), Core CPI, and Non-Core CPI (Raw Food, Energy) by forecasting their underlying components using `auto_ARIMA` and `Naive` models.

## Phase 1: Data Acquisition
**Agent**: `@data_fetcher`

1. **Fetch CPI Indices**: Retrieve the monthly CPI series from the CEIC API based on the `cpi_indices` mapping defined in `src/pipeline/cpi_forecast/config/cpi_mapping.json`.
2. **Fetch CPI Weights**: Retrieve the monthly CPI weights from the CEIC API based on the `cpi_weights` mapping defined in the same JSON config.
3. **Fetch Exogenous Data**: Load the Dubai Oil Price Prediction results (from the `energy_price_forecast` pipeline outputs, typically located at `output/data/energy_price_forecast/dubai_oil_forecast_production.csv`).
4. **Cache Data**: Save the raw data to `database/cpi_forecast/cpi_forecast.db`.

## Phase 2: Data Transformation & Reverse Engineering
**Agent**: `@data_transformer`

1. **Filtering**: Filter the raw CPI and Weight data to retain only the essential components required for prediction (as defined in the `prediction_targets_filter` mapping in the config).
2. **Reverse Engineering Weights**: 
   - `CPI: Weights: Housing & Furnishing (HF): Utilities` = **Non Core CPI: Weights: Raw Food and Energy: Energy** - **CPI: Weights: TC: Vehicles & Vehicle Operation: Motor Fuel**
   - `CPI: Weights: Housing & Furnishing (HF): ex Utilities` = **CPI: Weights: Housing & Furnishing (HF)** - `CPI: Weights: Housing & Furnishing (HF): Utilities`
   - `CPI: Weights: Transport & Communication (TC): ex Motor Fuel` = **CPI: Weights: Transport & Communication (TC)** - **CPI: Weights: TC: Vehicles & Vehicle Operation: Motor Fuel**
3. **Reverse Engineering Indices**:
   - For **Housing & Furnishing (HF)** group:
     - `CPI: Weights: Housing & Furnishing (HF): Utilities` = **'CPI: HF: Electricity, Fuel, Water Supply'**
     - Derive `CPI: Weights: Housing & Furnishing (HF): ex Utilities` from **'CPI: HF: Electricity, Fuel, Water Supply'** and **'CPI: Housing & Furnishing (HF)'**
   - For **Transport & Communication (TC)** group:
     - `CPI: Weights: Transport & Communication (TC): Motor Fuel` = **'CPI: TC: Vehicles & Vehicle Operation: Motor Fuel'**
     - Derive `CPI: Weights: Transport & Communication (TC): ex Motor Fuel` from **'CPI: Transport & Communication (TC)'** and the Motor Fuel index.
4. **Resampling Standard**: Ensure all data is monthly and stored in Wide Format (dates as rows, variables as columns).

## Phase 3: Modeling & Forecasting
**Agent**: `@econometrician`

1. **Forecast Indices (`auto_ARIMA`)**:
   - Forecast the CPI indices for all base components using `auto_ARIMA`.
   - *Exogenous Variable*: For `Transport & Communication: Motor Fuel`, incorporate the exogenous Dubai Oil Price Prediction data into the ARIMAX estimation.
2. **Forecast Weights (`Naive`)**:
   - Apply a Naive forecasting method (e.g., last observed value) to project the weights forward for each component.

## Phase 4: Aggregation
**Agent**: `@data_transformer`

1. **Compute Composites**:
   Using the forecasted component indices and their forecasted weights (defined by `composite_grouping` in the config JSON), calculate:
   - **Core CPI**: Weighted sum of (Seasoning and Condiments, Non Alcoholic Beverages, Sugar Product, Prepared Food, Apparel & Footwears, Housing & Furnishing: ex Utility, Medical & Personal Care, Transport & Communication: ex Motor Fuel, Recreation/Reading/Education/Religion, Tobacco & Alcoholic Beverages).
   - **Non-Core CPI: Raw Food**: Weighted sum of (Rice/Flour/Cereal, Meats Poultry & Fish, Eggs and Dairy Products, Vegetables and Fruits).
   - **Non-Core CPI: Energy**: Weighted sum of (Housing & Furnishing: Utility, Transport & Communication: Motor Fuel).
   - **Headline CPI**: Weighted sum of Core CPI and Non-Core CPI components.
2. **Frequency Resampling (Quarter-End)**:
   - Resample the monthly forecasted series into Quarterly frequency using strict Quarter-End ('QE') alignment.
   - Aggregate both Quarterly and Annual frequency series by averaging the constituent monthly observations.

## Phase 5: Output Generation
**Agent**: `@report_writer`

1. Export the monthly, quarterly, and annual predictions of Headline CPI, Core CPI, Non-Core CPI (Raw Food), and Non-Core CPI (Energy) into CSV files (wide format) at `output/data/cpi_forecast/`.
2. Update `PROJECT_STATE.json` using `src/utils/registry.py` to correctly log the new analytical datasets.

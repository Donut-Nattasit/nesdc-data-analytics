---
name: energy-price-forecast-lr
description: >
  Executes the long-range (LR) NESDC CPI forecasting pipeline extending to December 2031 using exogenous Dubai Crude prices, spliced geopolitical food shocks, and smooth exponential adjustments for selected indicators.
---

# Long-Range CPI Forecasting Pipeline Skill (energy_price_forecast_LR)

## Purpose
This skill orchestrates the long-range forecasting workflow of the NESDC Consumer Price Index (CPI) through December 2031. It allows analysts to execute scenario analyses on inflation rates using:
1. Long-range exogenous Dubai Crude spot prices (`dubai_oil_price_forecast_LR.xlsx`).
2. Spliced geopolitical price shock trajectories for the Prepared Food CPI index (`prepared_food_shock_comparison.csv`).
3. Smooth exponential growth adjustments to correct long-run forecast trends for selected component indicators.

---

## Execution Protocol

### Step 1 — Verify Inputs & Data Sources
Before running the pipeline, ensure the following input files are available and updated:
* **Exogenous Dubai Oil Price Forecast**: `input/oil_price_forecast_LR/dubai_oil_price_forecast_LR.xlsx` (must contain monthly forecasts through December 2031).
* **Prepared Food Shock Comparison**: `output/data/prepared_food_shock/prepared_food_shock_comparison.csv` (contains the shocked geopolitical trajectory `Prepared_Food_Index_shock` for June 2026 – December 2027).

### Step 2 — Run the Orchestrator
Execute the pipeline orchestrator in PowerShell from the project root directory:
```powershell
$env:PYTHONPATH='.'; $env:PYTHONUTF8='1'; .\.venv\Scripts\python.exe src/pipeline/energy_price_forecast_LR/orchestrator.py
```
This runs the full workflow:
1. **Prepare Data (`prepare_data.py`)**: Fetches CEIC historical data and builds `cpi_historical_master.csv`.
2. **Forecast Model (`predict_model.py`)**:
   * Fits univariate auto-ARIMA models for 15 CPI components and an ARIMAX model with exogenous Dubai prices for the Motor Fuel component.
   * Splices the Prepared Food shock index for June 2026 – December 2027, and propagates the shocked level smoothly through 2031 using baseline MoM growth rates.
   * Adjusts the growth trajectories of **Medical Personal Care** (target +1.0% annual) and **Apparel Footwears** (target +0.2% annual) starting from June 2026 using an exponential transition function with a 12-month half-life:
     $$c_k = c_{\text{LR}} \times (1 - e^{-\lambda \times k})$$
   * Re-aggregates composite indices (Core, Headline, Raw Food, Energy).
   * Generates monthly, quarterly (QE mean), and annual (YE mean) forecast tables and databases.
3. **Generate Charts (`generate_charts.py`)**: Renders line charts for aggregates and components.
4. **Generate Report (`generate_report.py`)**: Compiles the comprehensive briefing report.

---

## Outputs & Locations

*   **Report**: `report/energy_price_forecast_LR/energy_price_forecast_LR.md`
*   **Charts**: `output/chart/energy_price_forecast_LR/` (contains forecast lines, weight pies, and YoY growth bar charts)
*   **Datasets**: `output/data/energy_price_forecast_LR/` (contains monthly, quarterly, and annual `.csv` files)
*   **Database**: `database/energy_price_forecast_LR/energy_price_forecast_LR.db` (contains monthly, quarterly, and annual SQLite tables)
*   **Registry Status**: Programmatic helper updates `PROJECT_STATE.json` automatically on run.

---

## Troubleshooting

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| `FileNotFoundError` for food shock comparisons | The `prepared_food_shock` scenario pipeline hasn't been run yet | Run the `prepared_food_shock` pipeline first to generate `prepared_food_shock_comparison.csv` under `output/data/prepared_food_shock/`. |
| `KeyError` for historical master data | The date range of historical master data does not match the forecast start date | Clean the SQLite cache or run the pipeline data preparation step manually. |

---
name: ex_im_price_forecast
description: >
  Monthly pipeline execution for NESDC Export & Import Price Analysis & Forecasts.
  Handles API data retrieval from BOT and CEIC, rolling-validation, cointegration modeling with Dubai Crude Oil, and report compilation.
---

# Export & Import Price Monthly Pipeline Skill

## Purpose
This skill orchestrates the entire monthly workflow for the NESDC Export & Import Price Analysis & Forecasts project. It retrieves historical indices and weights from BOT and CEIC databases, estimates forecasts using univariate and exogenous models, aggregates components using volume-weighted resampling, and compiles the final Special Economic Brief.

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
2. Verify that the upstream `energy_price_forecast` output (`output/data/energy_price_forecast/dubai_oil_forecast_production.csv`) covers **at minimum the same horizon** as the confirmed Ex/Im horizon. If it is shorter, advise the user to re-run `energy_price_forecast` with a matching or longer horizon first.
3. Pass the horizon value to all relevant pipeline scripts as appropriate.
4. Only then proceed to **Step 1** of the Monthly Update Workflow below.

---

## 📅 Monthly Update Workflow

Follow this 3-step workflow to update the entire workspace:

### Step 1: Check Dependencies and Inputs
The exogenous forecasting models for energy-linked sectors (Mineral Product and Fuel - MF, and Fuel Product - FP) rely on crude oil forecasts. Before running this pipeline, ensure the user has executed the Dubai Oil forecasting pipeline:
- Check that `output/data/energy_price_forecast/dubai_oil_forecast_production.csv` exists and contains the latest spot projections.

### Step 2: Trigger the Automated Pipeline
Execute the complete pipeline script from the root workspace directory using PowerShell:

```powershell
cd src\pipeline\ex_im_price_forecast
.\run_pipeline.ps1
```

*Alternative (standard CMD/PowerShell from workspace root):*
```powershell
$env:PYTHONPATH='.'; .\.venv\Scripts\python.exe src/pipeline/ex_im_price_forecast/orchestrator.py
```

### Step 3: Verify and Review Outputs
Upon successful completion, the pipeline automatically:
1. Fetches historical actual indices and weights from the **Bank of Thailand (BOT) API** and **CEIC Database API**.
2. Computes quantity indices and resamples data into wide format.
3. Renders 9 distinct historical visualizations showing index paths, weights, and contributions.
4. Performs rolling window out-of-sample optimization to select the best-performing univariate model (`statsforecast` models like AutoARIMA, AutoETS, ARIMA with trend) for each component.
5. Calibrates exogenous cointegrating regressions (`SARIMAX` or `ARDL`) against the forecasted Dubai Crude Oil path for energy-linked components.
6. Computes raw composites, applies splicing ratio adjustments, and projects the official BOT indices.
7. Executes volume-weighted quarterly and annual resampling.
8. Re-compiles the final **Special Economic Brief** report with updated tables and charts.
9. Registers the newly generated datasets, models, and visualizations in `PROJECT_STATE.json`.

Review the updated report and charts:
*   **Special Economic Brief**: `report/ex_im_price_forecast/ex_im_price_forecast.md`
*   **Composite Forecast Chart**: `output/chart/ex_im_price_forecast/export_import_price_forecast_composites.png`
*   **Quarterly YoY Growth Chart**: `output/chart/ex_im_price_forecast/export_import_price_forecast_quarterly_yoy.png`
*   **Annual YoY Growth Chart**: `output/chart/ex_im_price_forecast/export_import_price_forecast_annual_yoy.png`
*   **Quantity Projections Chart**: `output/chart/ex_im_price_forecast/export_import_price_forecast_quantities.png`

---

## 🛠️ Centralized Pipeline Components

The pipeline runs the following 6 scripts in sequential order:

| Step | Phase | Script File | Key Responsibilities | Primary Output |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Ingest** | `prepare_data.py` | Queries BOT and CEIC APIs; merges series; computes quantity indices; saves wide monthly and quarterly datasets. | `output/data/ex_im_price_forecast/export_import_price_monthly_wide.csv` |
| **2** | **Visualize** | `plot_charts.py` | Plots historical price paths, weights structure, sub-component weights, and component growth contributions (Charts 1-9). | `output/chart/ex_im_price_forecast/*.png` (Charts 1-9) |
| **3** | **Model** | `forecast_statsforecast.py` | Evaluates univariate forecasting models (Naive, SNaive, AutoETS, HoltWinters, AutoARIMA) on expanding rolling windows. | `output/data/ex_im_price_forecast/export_import_price_forecast_statsforecast.csv` |
| **4** | **Model** | `forecast_exogenous.py` | Fits and optimizes exogenous cointegrating models (ARIMAX, ARDL) against Dubai crude price forecast for MF and FP target series. | `output/data/ex_im_price_forecast/export_import_price_forecast_statsforecast.csv` (overwritten) |
| **5** | **Aggregate** | `aggregate_and_plot.py` | Computes raw composites; performs level-splicing ratio calibrations; projects official BOT index; plots composite paths. | `output/chart/ex_im_price_forecast/export_import_price_forecast_composites.png` |
| **6** | **Report** | `resample_forecasts.py` | Forecasts trade quantity indices; resamples prices to volume-weighted quarterly and annual series; plots YoY growth; updates report. | `report/ex_im_price_forecast/ex_im_price_forecast.md` |

---

## 🔒 Freshness, Cache, & Dependencies

*   **Pipeline database**: Stored at `database/ex_im_price_forecast/ex_im_price_forecast.db`.
*   **BOT API Caching**: Bank of Thailand series are queried using `BOTClient` and cached locally inside the SQLite database to avoid redundant network hits.
*   **CEIC Integration**: Requires configured internet access to retrieve indices and weights. Parallel downloading with historical extensions is used.
*   **Exogenous Dependency**: The pipeline will raise a warning/error if `output/data/energy_price_forecast/dubai_oil_forecast_production.csv` is not found, as it is required by `forecast_exogenous.py` to project energy-linked indices.

---

## Troubleshooting

| Issue | Resolution |
|-------|-----------|
| Missing Dubai Oil forecast file | Run the `energy_price_forecast` pipeline first to populate the Dubai crude spot price forecast dataset. |
| CEIC API fetch fails | Ensure internet access is available and that CEIC SDK configurations are correct. |
| Pipeline fails to find Python | Verify that the virtual environment is set up at `.\.venv\` in the workspace root directory. |
| SQL Table lock / DB busy | Close any SQLite visualizers or other scripts connecting to `ex_im_price_forecast.db`. |

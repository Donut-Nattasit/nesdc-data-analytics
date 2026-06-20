---
name: deflator-prediction
description: >
  Executes the NESDC GDP Deflator forecasting pipeline. Use to fetch Thailand's quarterly GDP deflator from CEIC, build a log-log auto-ARIMAX model driven by forecasted CPI (with prepared-food shock), export and import price indices, and compile the deflator prediction report with quarterly/annual YoY projections and a diagnostics appendix.
---

# Deflator Prediction Pipeline Skill

## Purpose
This skill forecasts Thailand's **GDP Deflator** (CEIC series `367523747`, quarterly index) through the exogenous-data horizon (currently 2027-Q4). It fits a single **log-log auto-ARIMAX** model — `log(deflator)` regressed on three log-transformed, already-forecasted exogenous price indices — back-transforms the forecast to index levels, and reports results as **year-on-year (YoY) growth**. It sits downstream of the CPI and trade-price pipelines and feeds the umbrella `thailand_price_system`.

## Dependencies (must exist before running)
The pipeline consumes the *forecasted* outputs of upstream pipelines plus two raw CEIC series fetched directly:

| Input | Column(s) used | Source |
| :--- | :--- | :--- |
| CEIC `367523747` | target deflator | fetched directly (cached to pipeline DB) |
| CEIC `541395757` (Consumer Price Index, back to 1976) | actual headline CPI — **historical** exogenous | fetched directly |
| `output/data/prepared_food_shock/prepared_food_shock_comparison.csv` | `Headline_CPI_shock` — chained onto actual CPI by QoQ growth for the **forecast** window | `/food-shock` (needs `/cpi-forecast`) |
| `output/data/ex_im_price_forecast/export_import_price_forecast_quarterly.csv` | `bot_export_price_index`, `bot_import_price_index` | `/ex-im-forecast` |

**CPI splice:** to maximise history, the actual long-run headline CPI (`541395757`) is used over the estimation period and the prepared-food *shock* forecast is chained on by quarter-on-quarter growth for the forecast quarters (the two are ~99.95% correlated over their overlap). The estimation sample therefore starts at **2000-Q1** (bounded by the export/import indices), not 2018. The forecast horizon is bounded by the shortest exogenous forecast (currently 2027-Q4).

## Decision Tree: Dependency & Horizon Validation
```
                       Check exogenous inputs exist
                                    │
            ┌───────────────────────┴───────────────────────┐
            ▼ (Yes)                                          ▼ (No)
   Check exog horizon extends                     [ABORT: run /food-shock and
   beyond deflator history end                     /ex-im-forecast first]
            │
    ┌───────┴────────┐
    ▼ (Yes)          ▼ (No)
 [Proceed]     [ABORT: re-run upstream pipelines with longer horizon]
```

## Execution Protocol

### Step 1 — Dependency Pre-Check
* Confirm the two exogenous CSVs above exist and extend past the deflator's last historical quarter.

### Step 2 — Run the Pipeline Orchestrator
```powershell
$env:PYTHONPATH='.'; .\bin\python.ps1 src/pipeline/deflator_prediction/orchestrator.py
```
This runs `prepare_data` (CEIC fetch + quarterly merge) then `predict_model` (log-log auto-ARIMAX + diagnostics). Outputs:
* `output/data/deflator_prediction/deflator_forecast_quarterly.csv` and `deflator_forecast_annual.csv`
* `output/model_summary/deflator_prediction/{stationarity_tests,arimax_summary,residual_diagnostics}.txt`

### Step 3 — Charts (delegate to `viz-expert`, mandatory)
Generate into `output/chart/deflator_prediction/`: quarterly YoY line with 95% CI band (`deflator_quarterly_yoy.png`), annual YoY bars (`deflator_annual_yoy.png`), and deflator-vs-exogenous co-movement (`deflator_vs_exog.png`).

### Step 4 — Report (delegate to `report-writer`)
Compile `report/deflator_prediction/deflator_prediction.md` — Executive Summary, Methodology, Estimated Drivers (elasticities), Quarterly & Annual YoY tables/charts, Policy Implications, and Appendix A/B/C pasted verbatim from the `model_summary` text files.

## Notes
* **Tables and charts are reported in YoY growth, not index levels** (per analyst preference).
* Modeling is done **in log space** (log-log elasticity form); CIs are back-transformed via `exp()`.
* Residual diagnostics drop the first `d + m·D` seasonal-differencing burn-in residuals before Ljung-Box/Jarque-Bera.

## Troubleshooting

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| `FileNotFoundError` on a CPI or trade-price CSV | Upstream pipeline not run | Run `/food-shock` and `/ex-im-forecast` first. |
| Estimation sample shorter than expected | Export/import indices (start 2000) bound the joint sample | Expected — sample starts 2000-Q1. The actual CPI `541395757` reaches back to 1976, so it is not the binding constraint. |
| Discontinuity at the forecast splice | Actual CPI and shock-forecast bases diverged | Check the overlap ratio in `prepare_data.py`; they should be ~1.001. The splice chains QoQ growth, so a base mismatch does not jump the level. |
| CEIC fetch fails | API/proxy issue or missing `CEIC_API_KEY` | The pipeline falls back to the cached `database/deflator_prediction/deflator_prediction.db`; verify `.env` and connectivity to refresh. |
| Residual autocorrelation flagged | Burn-in residuals not dropped, or genuine misspecification | Confirm burn-in trimming in `predict_model.py`; if genuine, widen the `auto_arima` search space. |

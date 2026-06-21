# CQM — Python Pipeline (operational guide)

The Current Quarterly Model ported from EViews to Python. For the **methodology** (what the
model is, variable naming, bridge equations, data, known issues), read
[`CQM_MODEL_MANUAL.md`](CQM_MODEL_MANUAL.md). This file covers **how to run it**.

Code: [`src/pipeline/cqm/`](../../src/pipeline/cqm/) · Source materials: `input/CQM/`

---

## What it produces

A monthly **nowcast / short-horizon forecast of Thai GDP** — by 20 production industries
and by expenditure (C, G, I, X, M), in real / nominal / deflator terms, as YoY and
QoQ-annualised (sa) growth.

---

## Module map

| Module | Role |
|---|---|
| `config.py` | Parses `metadata.xlsx` + the CEIC numeric IDs embedded in the Excel headers into structured config. Classifies each series as **fetched** (CEIC), **derived** (a formula of others), or **manual** (GIFDATA, not on CEIC). Parses the 60 bridge equations, 54 identities, ARIMA & X12 specs. |
| `fetch_data.py` | Pulls every fetchable monthly indicator + quarterly NIPA series from CEIC → wide CSVs + SQLite cache (`database/cqm/cqm_data.db`). |
| `forecast_indicators.py` | Per indicator: **X13** seasonal adjustment (`bin/x13as.exe`, STL fallback) + **auto_arima** forecast → quarterly `_FQ` / `_3m_FQ` bridge inputs. *Slow step (~10–15 min for ~116 series).* |
| `bridge_model.py` | Identity solver + bridge-equation OLS estimation + iterative forecast + univariate auto_arima fallback for components whose regressors are unavailable. |
| `orchestrator.py` | **Entry point.** Wires everything, level-anchors GDP to the official NESDC totals, writes the output tables and run summary. |

---

## How to run

Always use the project launcher (resolves the venv, sets PYTHONPATH/UTF-8):

```powershell
# 1. Refresh data from CEIC (fast, ~1 min)
& '.\bin\python.ps1' 'src\pipeline\cqm\fetch_data.py'

# 2. Seasonally adjust + ARIMA-forecast the monthly indicators (SLOW, ~10–15 min)
& '.\bin\python.ps1' 'src\pipeline\cqm\forecast_indicators.py'

# 3. Estimate bridge equations, solve, build GDP + growth tables (fast)
& '.\bin\python.ps1' 'src\pipeline\cqm\orchestrator.py'
```

Steps 1–2 cache to CSV, so re-running the orchestrator (step 3) alone is fast while iterating.

---

## Outputs

| File | Content |
|---|---|
| `output/data/cqm/monthly_indicators_raw.csv` | Raw monthly indicators (wide, `X_` columns) |
| `output/data/cqm/nipa_quarterly_raw.csv` | Raw quarterly NIPA actuals (wide, Y/Z columns) |
| `output/data/cqm/indicators_quarterly_FQ.csv` | SA + forecast quarterly indicator inputs (`_FQ`, `_3m_FQ`) |
| `output/data/cqm/nipa_forecast_levels.csv` | Full NIPA frame, actual + forecast levels |
| `output/data/cqm/cqm_growth_quarterly.csv` | Key aggregates — YoY % and QoQ-saar % |
| `output/data/cqm/cqm_growth_annual.csv` | Annual YoY |
| `output/model_summary/cqm/cqm_run_summary.txt` | Diagnostics: bridge R², fallback list, horizon |

---

## Current status (v1) and known limitations

The pipeline runs **error-free end to end** on live CEIC data (NIPA → 2026Q1, monthly →
2026-05). First run: real GDP nowcast ≈ **2026Q2 +2.7%, Q3 +3.4%, Q4 +2.1% YoY**.

v1 caveats — these define the planned quality-improvement stage:

- **Deflator (ZPS) bridge equations are weak** (near-zero R²) — they are the 2016 differenced
  specs and need rework. The export/import nominal equations fit well (R² > 0.9).
- **4 components use univariate fallback** (`YNS031G`, `YNS032G`, `ZNS060`, `ZNS110`) — the
  GIFDATA government-investment and financial-sector ones, per the agreed placeholder strategy
  (see manual §7).
- **Near-term import growth looks high**; long-horizon series mean-revert (expected for ARIMA
  without exogenous drivers). The near-term nowcast quarters are the reliable zone.
- Bridge specifications still use the **legacy 2016 regressor choices** (not yet re-optimised).
- No `/cqm` slash command yet — runs as scripts.

---

## Maintenance notes

- **Re-fetch refresh:** run `fetch_data.py` → `forecast_indicators.py` → `orchestrator.py`.
- **Forecast horizon:** controlled by `forecast_quarters` in `orchestrator.run()` /
  `forecast_indicators.process_indicators()` (default 5 quarters beyond last NIPA quarter).
- **Government investment:** when NESDC supplies real monthly GCON/GEQ disbursement, add it as a
  manual input and remove those four components from the univariate fallback.
- The model config is data-driven from `metadata.xlsx` — to add/replace an indicator or bridge
  equation, edit that file rather than the code where possible.

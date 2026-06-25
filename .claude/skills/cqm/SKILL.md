---
name: cqm
description: >
  Runs the NESDC Current Quarterly Model (CQM) — the monthly bottom-up nowcast of Thailand's current-quarter GDP by 20 production sectors and by expenditure (C, G, I, X, M), built from CEIC monthly indicators via bridge equations. Make sure to use this skill whenever the user asks to run, refresh, update, or re-run the CQM, to nowcast or estimate this quarter's Thai GDP, to produce the monthly GDP nowcast report, or mentions the Current Quarterly Model / bridge-equation GDP model — even if they don't explicitly say "use the cqm skill." Covers a full data-refresh run, a quick report-only re-run, and a no-data-refresh backtest.
---

# CQM — Current Quarterly Model Pipeline Skill

## Purpose
CQM **nowcasts Thailand's current-quarter GDP every month** as new monthly indicators are released. It forecasts the not-yet-finished monthly indicators forward (X13 seasonal adjustment + `auto_arima`), aggregates them to quarterly, pushes them through ~60 OLS **bridge equations**, closes the National Accounts with accounting identities, and level-anchors the result to the official NESDC GDP totals. Output: real / nominal / deflator GDP by 20 production sectors and by expenditure, as YoY % and QoQ-annualised (sa) growth, plus a visualization-first report.

**Scope — current quarter only (≤ 1 quarter ahead).** CQM is deliberately a *nowcaster*: it estimates the single quarter immediately after the latest official GDP. It is **not** a multi-quarter forecaster — longer horizons are a separate model's job. This is enforced by `BridgeEngine(max_forecast_quarters=1)` and `orchestrator.run(forecast_quarters=1)` defaults. Do **not** raise the horizon for production nowcasts; un-cap it *only* for backtesting.

**Read first:** `docs/cqm/CQM_MODEL_MANUAL.md` (methodology, variable naming, bridge equations) and `docs/cqm/README.md` (operational detail). The methodology is also mirrored in Claude memory under `reference-cqm-model`. Code lives in `src/pipeline/cqm/`.

## When to run which mode
Pick the mode from what the user is doing. **Why?** The indicator-forecast step (X13 + `auto_arima` over ~116 series) takes ~10–15 minutes; skipping it when the data hasn't changed turns a coffee-break run into a few seconds, which matters when iterating on the report.

```
                      Is there new monthly / NIPA data to pull from CEIC?
                                          │
            ┌─────────────────────────────┴─────────────────────────────┐
            ▼ (Yes — monthly release, new GDP print)                     ▼ (No — just tweaking report/charts)
                    FULL RUN                                          QUICK RUN
        fetch → forecast → orchestrate                       orchestrate → report
        → report   (~15 min)                                 (cached _FQ inputs, seconds)
```

A new official GDP release also means the model **re-anchors history** — that always needs a FULL run so the new actual quarter flows through.

## A. Full run (monthly refresh)
Use when monthly indicators updated on CEIC, or NESDC published a new GDP figure. Always invoke Python through the project launcher (it resolves the off-OneDrive venv and sets PYTHONPATH/UTF-8).

### Step 1 — Fetch from CEIC (fast, ~1 min)
```powershell
& '.\bin\python.ps1' 'src\pipeline\cqm\fetch_data.py'
```
Pulls every fetchable monthly indicator + quarterly NIPA series → wide CSVs in `output/data/cqm/` and SQLite cache `database/cqm/cqm_data.db`. If CEIC is unreachable it falls back to the cached DB.

### Step 2 — Seasonally adjust + ARIMA-forecast indicators (SLOW, ~10–15 min)
```powershell
& '.\bin\python.ps1' 'src\pipeline\cqm\forecast_indicators.py'
```
Per indicator: X13 (`bin/x13as.exe`, STL fallback) seasonal adjustment + `auto_arima` extension → quarterly `_FQ` / `_3m_FQ` bridge inputs in `indicators_quarterly_FQ.csv`. This is the only slow step; it caches, so later report iterations reuse it.

### Step 3 — Solve the model (fast)
```powershell
& '.\bin\python.ps1' 'src\pipeline\cqm\orchestrator.py'
```
Estimates bridge equations, runs the iterative quarter solve, applies identities, level-anchors GDP to official `ZRS1000`/`ZNS1000`. Outputs: `nipa_forecast_levels.csv`, `cqm_growth_quarterly.csv`, `cqm_growth_annual.csv`, and `output/model_summary/cqm/cqm_run_summary.txt`. The console prints the headline nowcast — capture it.

Then continue to **Section C (report)**.

## B. Quick run (report-only)
Use when the data is unchanged and the user just wants to regenerate charts or rebuild the report (e.g. wording, layout). Skip Steps 1–2; the `_FQ` inputs are already cached.
```powershell
& '.\bin\python.ps1' 'src\pipeline\cqm\orchestrator.py'
```
Then continue to **Section C**.

## C. Report assembly (always after a solve)

### Step 1 — Prepare report data
```powershell
& '.\bin\python.ps1' 'src\pipeline\cqm\report_prep.py'
```
Writes `output/data/cqm/report_elements.csv` (per-element levels + YoY, `is_forecast` flag) and the human-readable bridge tables `output/model_summary/cqm/bridge_summaries_readable.md` (data codes translated to plain names — the report appendix).

### Step 2 — Charts (delegate to `viz-expert`, mandatory)
**All charts go through `viz-expert`** — never write matplotlib inline. This guarantees NESDC palette, FC Vision font, and layout compliance. The five charts (into `output/chart/cqm/`), each showing history + the **single** saffron current-quarter nowcast marker:

| File | Content |
|---|---|
| `gdp_headline.png` | Real GDP level + YoY bars, nowcast annotated |
| `production_grid.png` | 4×5 grid — 20 sectors, real GVA |
| `production_yoy_grid.png` | 20 sectors, YoY % |
| `expenditure_grid.png` | C/G/I/X/M components, real |
| `gdp_deflator.png` | GDP deflator + nominal vs real |

Tell `viz-expert` the nowcast quarter is the only forecast point (no multi-quarter dashed path) — it reads `report_elements.csv` where `is_forecast` is true for exactly one quarter.

### Step 3 — Build the report
```powershell
& '.\bin\python.ps1' 'src\pipeline\cqm\build_report.py'
```
Assembles `report/cqm/CQM_Nowcast_Report.md` — fully data-driven from the forecast quarter present in the data (executive summary, headline GDP, production & expenditure sections, deflator, quality-at-a-glance, caveats, and Appendix B = readable bridge summaries).

### Step 4 — Export to HTML (delegate to `md-to-html`)
Produce the self-contained, shareable `report/cqm/CQM_Nowcast_Report.html` (base64-embedded charts).

### Step 5 — Report the nowcast
Tell the user the headline in plain terms: e.g. *"2026Q2 real GDP nowcast: +2.7% YoY (+1.6% QoQ saar)."* Point them to the HTML report and the run summary.

## D. Backtest (only when explicitly asked)
A backtest needs the multi-quarter cap removed. Run the engine with `max_forecast_quarters=None` over an expanding window — **this is the one case where the horizon cap is lifted**, and it must never be the default for a production nowcast. The established baseline: 17-quarter window (2022Q1–2026Q1), CQM real-GDP RMSE ≈ 0.64 pp vs ~1.06–1.14 pp for naive benchmarks (~40 % better). See `output/model_summary/cqm/cqm_quality_report.md`.

## Key facts to remember
- **GIFDATA placeholder.** Government investment (construction/equipment disbursement) is NESDC-internal, not on CEIC. Four components — `YNS031G`, `YNS032G`, `ZNS060`, `ZNS110` — currently use a univariate `auto_arima` fallback. When the user supplies real monthly GCON/GEQ, wire it in and drop those from the fallback.
- **VAT is dead.** `17_T_MasterV` ended 2016 and is all `#n.a.`. The live path is `T_PROD_G` (government-expenditure), program 06 skipped. Do *not* confuse with `X_VATHOTEL` (CEIC `THWAAAMJUAAAFD`), an active hotel/restaurant index that is kept.
- **Deflator block is weak.** The ZPS (price) bridge equations have near-zero out-of-sample skill — treat deflator nowcasts as indicative only. Rebuilding them is the top item in `docs/cqm/IMPROVEMENT_STRATEGY.md`.
- **Config is data-driven.** To add/replace an indicator or bridge equation, edit `input/CQM/metadata.xlsx` rather than the code where possible.

## Troubleshooting

| Issue / Error | Cause | Resolution |
|---|---|---|
| `FileNotFoundError: indicators_quarterly_FQ.csv` on a quick run | Step 2 (forecast) never ran on this machine/data | Do a full run once (Section A) to produce the cached `_FQ` inputs. |
| `forecast_indicators.py` extremely slow / appears hung | Normal — X13 + `auto_arima` over ~116 series is the ~10–15 min step | Let it finish; it caches so you only pay this once per data refresh. |
| X13 errors / `x13as.exe` not found | Missing/locked binary | It falls back to STL automatically; check `bin/x13as.exe` exists if you need true X13. |
| CEIC fetch fails | API/proxy issue or missing `CEIC_API_KEY` | Pipeline falls back to the cached `database/cqm/cqm_data.db`; verify `.env` and connectivity to refresh. |
| Report shows a multi-quarter forecast path | Horizon cap was lifted | Confirm `orchestrator.run(forecast_quarters=1)` and `BridgeEngine(max_forecast_quarters=1)`; the production scope is one quarter. |
| Nowcast quarter looks wrong | NIPA actuals stale | Re-run `fetch_data.py`; the nowcast is always the quarter *after* the last actual NIPA quarter. |
| `ModuleNotFoundError` / wrong Python | Called system Python directly | Always run through `.\bin\python.ps1`; never `.venv\Scripts\python.exe`. |

# CQM — Improvement Strategy

Prioritised plan to evolve the v1 Python port (which already beats naive benchmarks by
~40% on GDP-nowcast RMSE) into a robust production nowcasting system. Based on the
[quality report](../../output/model_summary/cqm/cqm_quality_report.md).

Each item is tagged **[impact / effort]**. Recommended order is top to bottom.

---

## Tier 1 — Correctness (do first; cheap, high trust)

### 1.1 Real-time (concurrent) seasonal adjustment **[high / medium]**
The v1 SA runs X13 on the full sample, giving a two-sided-filter peek at the future. For an
honest monthly nowcast, seasonally adjust each vintage using only data available at that
date (X13 concurrent mode, or re-run SA on the truncated series each period). Removes the
look-ahead bias in the backtest and makes reported skill real.

### 1.2 Fall back to univariate for no-skill bridges **[high / low]**
The 17 equations with OOS R² ≤ 0 do not beat their own mean. Add a rule: if a bridge's
expanding-window OOS R² ≤ 0 (or ≤ a small threshold), use the univariate auto_arima forecast
of that component instead of the bridge. Quick, guards against bad bridges dragging GDP.

### 1.3 Restore dynamic error structure **[medium / medium]**
The OLS port dropped the legacy AR/MA terms; Durbin–Watson shows residual autocorrelation
across the board (DW≈3.3 on strong fitters → add MA; DW<1 on weak ones → add AR). Refit
bridges as **SARIMAX(endog=ΔLHS, exog=indicators, order auto-selected)** so residuals are
white. Should lift the mid-tier equations.

---

## Tier 2 — Fix the weak blocks (high payoff)

### 2.1 Rebuild the deflator (ZPS) block **[high / high]**
10 of 17 no-skill equations are price deflators, most driven by a single generic CPI term
with spurious autocorrelation. Options (test competitively):
- **Decompose, don't model the ratio.** Forecast nominal (ZNS) and real (ZRS) separately and
  let the deflator fall out as ZNS/ZRS — often more stable than modelling ZPS directly.
- **Sector-specific prices.** Map each industry deflator to its own PPI/CPI sub-index instead
  of headline CPI (e.g. construction deflator ← construction materials PPI, already partly
  done; extend to all).
- **Log-level ARIMAX** with proper order selection rather than D4-of-3m-MA differencing.

### 2.2 Re-optimise bridge specifications (not just ARIMA orders) **[high / high]**
The regressor choices are frozen from 2016. Build an automated per-equation specification
search refit each quarter: candidate-regressor pool per component (current CEIC indicators),
selection by AICc / cross-validated OOS R² (stepwise or LASSO/elastic-net). Keeps the model
current as data sources evolve and replaces the weak service-sector equations.

### 2.3 Competitive ML cross-check per component **[medium / high]**
Per the workspace rule, run both `econometrician` (ARIMAX/ARDL) and `data-scientist`
(XGBoost / Ridge / MIDAS) for each forecast component and combine. Especially for the weak
service real industries (ZRS100/130/160/170/200) where linear bridges fail.

---

## Tier 3 — Data completeness

### 3.1 Build the financial-sector regressors **[medium / low]**
ZNS110 falls back to univariate only because `X_RAsset` / `X_RDeposit` were never built. They
derive from bank loans (CEIC `TKJAACAC`) and deposits (`TKJAACBA`), both already fetched —
add the derived real series and the bridge becomes usable.

### 3.2 Government investment (GIFDATA) **[medium / external]**
Replace the univariate placeholders for public construction (YNS031G), public equipment
(YNS032G), and construction-supply (ZNS060) once NESDC supplies real monthly government
construction & equipment disbursement. Wire it as a manual input feed.

### 3.3 Replace discontinued indicators **[low / medium]**
Audit regressors mapped to discontinued series (old TSSI, passenger departures, old PII) and
swap for current CEIC equivalents.

---

## Tier 4 — Robustness, validation, delivery

### 4.1 Full real-time backtest harness **[high / high]**
Generalise the current backtest to a true pseudo-real-time loop (truncate → concurrent SA →
ARIMA → bridge → GDP) over 20–40 quarters, reporting RMSE/MAE/bias and the **nowcast
evolution within a quarter** (how the estimate updates as months arrive). This is the
definitive quality metric and a great report exhibit.

### 4.2 Forecast uncertainty bands **[medium / medium]**
Propagate ARIMA + bridge prediction intervals to a GDP fan chart. Be explicit that beyond
~2 quarters the model is essentially ARIMA extrapolation (it mean-reverts).

### 4.3 Port the PCA / add a DFM top-down model **[medium / high]**
A top-down aggregate nowcast (PCA or Dynamic Factor Model on all indicators) as an
independent second opinion; combine with the bottom-up CQM.

### 4.4 Investigate the near-term import spike **[low / low]**
v1 shows high 2026Q2–Q3 import growth; check the nominal import bridge vs the import value
index base effect.

### 4.5 Productionise **[low / low]**
Wire a `/cqm` skill + slash command; cache vintages; one-command monthly refresh.

---

## Suggested next sprint
1.2 (univariate guard) + 3.1 (financial regressors) + 1.3 (dynamic errors) are the
cheapest wins. Then 1.1 (real-time SA) for honesty, and 2.1 (deflator rebuild) for the
biggest quality gain. 4.1 (real-time backtest) underpins everything — build it early so each
change is measured.

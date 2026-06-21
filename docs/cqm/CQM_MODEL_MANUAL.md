# NESDC Current Quarterly Model (CQM) — Methodology Manual

> Rewritten in English from the original Thai manual
> (`input/CQM/Manual/1-Thai CQM manual thai.doc`, Thammasat University / ITeconomy
> Advisors, 2016), the EViews programs (`input/CQM/EViews Codes/01–13`), and
> `metadata.xlsx`. This is the authoritative reference — consult the original `.doc`
> only for the EViews-GUI screenshots/click steps.
>
> Companion documents: [`README.md`](README.md) (how to run the Python port).

---

## 1. What the model does (purpose)

CQM **nowcasts the current quarter's Thai GDP every month** as new monthly indicators
are released. It produces the full National Income (NIPA) account — GDP by **production
side** (20 ISIC industries) and **expenditure side** (C, G, I, X, M) — in nominal, real
(chain-volume measure, 2002 prices), and deflator terms, with QoQ-annualised (sa) and
YoY growth tables.

**Scope (decided 2026-06):** CQM is a **current-quarter nowcaster only** — it forecasts
the single quarter immediately after the latest official GDP (≤ 1 quarter ahead). It is
deliberately **not** used for multi-quarter projection; longer-horizon forecasts are
produced by a separate, dedicated model. (The engine *can* be un-capped for backtesting,
but production runs use a 1-quarter horizon: `max_forecast_quarters=1`.) It is re-run
**monthly** when any monthly indicator updates, and **re-anchored quarterly** when NESDC
releases a new GDP figure.

**Core idea — a bridge between fast data and slow data.** Quarterly GDP arrives slowly
and late; dozens of monthly indicators (industrial production, retail sales, tourist
arrivals, trade values, CPI/PPI, etc.) arrive sooner. CQM ties each slow GDP component
to fast monthly indicators through a **bridge equation**. Monthly indicators are first
seasonally adjusted and **forecast forward with ARIMA** to complete the not-yet-finished
quarter, then aggregated to quarterly; the bridge equations translate them into each GDP
component; accounting identities close the books.

**One sentence:** *forecast the monthly indicators → push them through bridge equations →
assemble the National Accounts → read off GDP growth.*

A companion **PCA** (Principal Component Analysis) model was a top-down cross-check that
forecasts aggregate Real GDP and the GDP deflator directly from the common signal across
all indicators. (Not yet ported to Python.)

---

## 2. Variable naming convention (memorise this)

NIPA series are renamed on import to a code of the form **`<S><F>S<nnn><suffix>`**:

- **Side letter (`S`)**
  - `Y…` = **expenditure side** (demand: C, G, I, X, M)
  - `Z…` = **production side** (supply: 20 industries)
- **Price-basis letter (`F`)**
  - `N` = **Nominal** (current prices)
  - `R` = **Real** (chain-volume measure, 2002 prices)
  - `P` = **Price / deflator** (`ZPSxxx = ZNSxxx / ZRSxxx × 100`)
- **3-digit code (`nnn`)** = component / industry (tables below)
- **Suffix**
  - `_U` = **unadjusted** (not seasonally adjusted). No `_U` ⇒ seasonally adjusted (sa).

Examples: `YNS010` = nominal private consumption · `YRS010` = real private consumption ·
`YPS010` = its deflator · `ZRS030` = real manufacturing GVA · `ZPS030` = manufacturing
deflator.

**Monthly indicators** are imported with an `X_` prefix (e.g. `X_TBPAA`). Their transform
suffix chain:

- `_SA` — seasonally adjusted (X13)
- `_FQ` — forecast-extended and aggregated to **quarterly**
- `_3m` — 3-month moving-average variant
- `D1…` = 1st difference (QoQ) · `D4…` = 4th difference (YoY)

So a typical bridge-equation regressor reads `D1X_TBPAA_SA_FQ` = "QoQ change in the
seasonally-adjusted, forecast, quarterly agricultural-production index."

### Expenditure (Y) component codes

| Code | Component |
|---|---|
| 010 | Private consumption |
| 020 | Government consumption |
| 030 | Gross fixed capital formation (GFCF); `031` construction, `032` equipment; suffix `P`=private, `G`=public |
| 040 | Change in inventories |
| **049** | **inventories + statistical discrepancy combined** — the "_49p" in program names |
| 060 | Exports (`061` goods, `062` services) |
| 070 | Imports (`071` goods, `072` services) |
| 080 | Expenditure-side GDP total |
| 090 | Statistical discrepancy |

### Production (Z) industry codes (ISIC)

| Code | Industry | Code | Industry |
|---|---|---|---|
| 010 | Agriculture | 110 | Financial & insurance |
| 020 | Mining | 120 | Real estate |
| 030 | Manufacturing | 130 | Professional/scientific |
| 040 | Electricity & gas | 140 | Administrative & support |
| 050 | Water & waste | 150 | Public admin & defence |
| 060 | Construction | 160 | Education |
| 070 | Wholesale & retail trade | 170 | Health |
| 080 | Transport & storage | 180 | Arts & entertainment |
| 090 | Accommodation & food | 190 | Other services |
| 100 | Information & communication | 200 | Households |

Aggregates: `1000` = total GDP · `1020` = non-agriculture · `1021` = industrial ·
`1022` = services · `540` = service-subsector sum.

---

## 3. Data inputs

| Input | Legacy file | Content | Source |
|---|---|---|---|
| Quarterly NIPA (~75–97 series) | `16_T_MasterQ_*.xls` | GDP by production & expenditure, nominal/real/sa | CEIC CDM `T_NIPAQ_All`; refresh each GDP release |
| Monthly indicators (~155 series) | `15_T_MasterM_*.xls` | IP, retail, tourism, trade, CPI/PPI, money, rates… | CEIC CDM `T_EXOM_all`; refresh weekly/monthly |
| VAT by sector | `17_T_MasterV_*.xls` | VAT revenue by ISIC | **DEPRECATED — see §7** |
| Government investment | `14_gifdata.wf1` | Govt construction/equipment disbursement | **NESDC-internal — manual update, see §7** |
| Variable map | `metadata.xlsx` | The model config: id → rename → X12 → diff → ARIMA spec → bridge eqn | — |

**Key fact:** the CEIC **numeric series IDs are embedded in the Excel header rows**, so the
monthly and quarterly data can be re-fetched from the CEIC API instead of manual Excel
updates. Only the GIFDATA government-investment series and a few discontinued series
genuinely need manual sourcing.

`metadata.xlsx` is the model's brain — four sheets:
- **Indicators** — each monthly series: CEIC mnemonic, rename, X12 mode, differencing, ARIMA order.
- **NIPA** — each GDP series: rename, identity ("Re-Calculate"), bridge equation.
- **VAT** — the (now-dead) VAT-by-sector mapping.
- **Govt** — the GIFDATA government-investment construction (`X_GCON`) & equipment (`X_GEQ`).

---

## 4. The legacy EViews pipeline (run order 01 → 13)

| # | Program | Does |
|---|---|---|
| 01 | `T_Assign.prg` | Sets ALL parameters: forecast date, workfile/db names, per-indicator data start/end, sample & forecast ranges. **The main file the user edits each run.** |
| 02 | `T_Profile.prg` | Creates the monthly & quarterly workfiles and databases. |
| 03 | `T_LoadRename_EXOM.prg` | Imports monthly indicators, renames with `X_` prefix. |
| 04 | `T_LoadRename_GOV.prg` | Imports NESDC-internal govt investment from `GIFDATA.wf1`. |
| 05 | `T_LoadRename_NIPA.prg` | Imports quarterly NIPA, renames to Y/Z…, builds identities. |
| 06 | `T_LoadRename_VAT.prg` | Imports VAT — **skip, deprecated.** |
| 07 | `T_ARIMA.prg` | Per indicator: X12 seasonal-adjust, difference, fit fixed-spec ARIMA, forecast to end of next quarter, build 3-month MA. |
| 08 | `T_PROD_G.prg` | **Production side.** Aggregate indicators to quarterly, estimate production bridge equations, solve GDP by 20 industries. `_G` = government-expenditure path (live); `_VAT` variant is dead. **Run before 09.** |
| 09 | `T_EXP_49p_G.prg` | **Expenditure side.** Estimate expenditure bridge equations for C/G/I/X/M. `_49p` = inventories + statistical discrepancy collapsed into one residual. |
| 10 | `T_AGGR_49p_G_SA.prg` | Aggregate quarterly→annual; compute **QoQ-annualised (sa)** growth. |
| 11 | `T_AGGR_49p_G_YOY.prg` | Same for **YoY** growth. |
| 12 | `T_NIPA_Tables_49p_G_SA.prg` | Export QoQ-annualised forecast tables. |
| 13 | `T_NIPA_Tables_49p_G_YOY.prg` | Export YoY forecast tables. |

(Original steps 14–17 are Excel display sheets linked to the exported tables — cosmetic.)
The Python port (see `README.md`) collapses 01–13 into five modules.

---

## 5. Bridge-equation methodology (the heart)

Each forecast NIPA component has an OLS bridge equation regressing its **quarterly
difference** on quarterly-aggregated, ARIMA-extended monthly indicators (plus optional
AR/MA terms and self-lags). Exact specs live in `metadata.xlsx` (NIPA sheet, "Estimate
Bridge Equation" column). Pattern: `e_<name>.ls <LHS> C <RHS…> ar(p) ma(q)`.

Representative equations:

- **Production, real (ZRS):**
  - `D1ZRS010 = f(D1·agricultural production index)` — agriculture
  - `D1ZRS030 = f(D1·BOT manufacturing production index)` — manufacturing
  - `D1ZRS020 = f(D1·natural-gas output)` — mining
  - `D1ZRS040 = f(D1·electricity consumption)` — electricity
  - `D1ZRS080 = f(D1·tourist arrivals, D1·petroleum)` — transport
- **Production, nominal (ZNS):**
  - `D4ZNS060 = f(D4·govt construction spend)` — construction
  - `D1ZNS090 = f(D1·hotel/restaurant index, D1·tourists)` — accommodation
- **Production, deflator (ZPS):** regressed on relevant CPI/PPI, e.g.
  `D1ZPS030 = f(D1·manufacturing PPI)`.
- **Expenditure (Y):**
  - consumption `D1YRS010 = f(D1·private consumption index)`; deflator `D1YPS010 = f(D1·CPI)`
  - exports goods `D1YNS061 = f(D1·BOP exports)`; export price `D1YPS061 = f(D1·export price index)`
  - imports analogous with BOP imports / import price index
  - government `D1YNS020 = f(D1·fiscal cash expenditure)`
  - public construction `D1YNS031G = f(govt construction)`, public equipment `D1YNS032G = f(govt equipment)`

After estimation, the model **solves** behavioural equations + identities to fill the
forecast quarters. Identities close the accounts, e.g.
`YNS049 = ZNS1000 − YNS010 − YNS020 − YNS030 − YNS060 + YNS070` (the inventory +
discrepancy plug), `ZPS1000 = ZNS1000 / ZRS1000 × 100` (GDP deflator).

**Two-sided structure.** The production side is solved first (GDP = sum of 20 industries);
the expenditure side is solved next, with the inventory-plus-discrepancy term (`049`)
backed out so the two sides reconcile.

**Modernisation note.** ARIMA orders and bridge specs were hard-coded around 2016. The
Python port re-fits ARIMA each run with `auto_arima` rather than freezing the old orders;
re-optimising the bridge specifications themselves is the planned quality-improvement step.

---

## 6. Companion PCA model (not yet ported)

`T_PCA_yyyymmdd.prg` uses the CQM ARIMA indicator forecasts to extract principal
components and forecast aggregate **Real GDP growth** and the **GDP deflator**
independently — a top-down sanity check on the bottom-up CQM. Lower priority; the
bridge-equation CQM is the primary deliverable.

---

## 7. Known issues, manual-update data, and deprecations

- **VAT data — DEPRECATED, safe to ignore.** All `17_T_MasterV` series end 2016-10 and the
  master file is all `#n.a.`. VAT only feeds the optional `T_PROD_VAT.prg` path; the **live
  path uses `T_PROD_G.prg`** (government-expenditure version), which needs no VAT. Skip
  program 06.
  > ⚠️ Do **not** confuse with `X_VATHOTEL` (CEIC `THWAAAMJUAAAFD`, "VAT of Hotel &
  > Restaurant Index") — that is a still-active CEIC index used in the accommodation bridge
  > equation. Keep it.
- **Government investment = the one real manual-update dependency.** `14_gifdata.wf1` holds
  NESDC-internal monthly **government construction & equipment disbursement**
  (`Gconcur, Gconcap, Geqcur, Geqcap → X_GCON, X_GEQ`). Not on CEIC. Drives the public
  construction (`YNS031G`), public equipment (`YNS032G`), and construction-supply (`ZNS060`)
  bridge equations. **NESDC must supply this monthly.** Interim fallback: univariate ARIMA on
  the component itself so the model still solves.
- **Discontinued / stale series** referenced by some equations: passenger departures
  TQJABBA/TQJABBB (ended 2016), TSSI sector series TOADACE* (ended 2019), old PII components
  TOYAI/TOYAJ/TOYAK (ended 2018), old RSI THMBFC, SOECON, RTI/WSI. Where a live bridge
  equation depends on one, substitute a current CEIC equivalent or drop the regressor when
  re-optimising.
- **Human errors in the legacy files** (the last maintainer was not a coder): duplicate CEIC
  IDs in the Excel headers, a contradictory double-definition of the `ZNS540`/`ZRS540` service
  aggregate, formula rows mixed into "rename" cells. The Python config parser handles these
  defensively.

---

## 8. Operational cadence

- **Weekly / monthly:** refresh monthly indicators (CEIC), advance the date parameters, re-run
  the indicator forecasts and the bridge solve.
- **Quarterly:** when NESDC publishes a new GDP figure, refresh the quarterly NIPA (CEIC),
  re-anchor history, re-optimise ARIMA + bridge equations, then run the full pipeline.

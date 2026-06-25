# Data Recipes — where each series comes from and how to get it

Use this when filling `config.ceic_series` and fetching. Delegate the actual API
calls to the **data-fetcher** agent; this file tells it *what* to look for.

## CEIC — resolving series IDs (do this once, then pin in config)

Search from the Bash tool, no script needed:
```
python src/api/ceic_client.py search "Indonesia Real GDP Growth" --limit 20
```
Prefer **World Trend Plus / Global Economic Monitor (GEM)** series — they are
cross-country comparable, so the same search pattern works for every country.
When a good match is found, **write its `series_id` into `config.ceic_series`**
so the next run skips the search entirely.

Search keywords per indicator (substitute the country name):

| config key | search keyword | freq | units |
|---|---|---|---|
| gdp_real_yoy_q | "{C} Real GDP Growth" / "{C} GDP YoY" | Q | %YoY |
| gdp_real_annual | "{C} GDP Constant Price" (annualise) | A | %YoY |
| gdp_exp_components | "{C} GDP Expenditure Constant" | Q | local / %YoY |
| gdp_prod_components | "{C} GDP Industry Constant" / "by sector" | Q | local / %YoY |
| exports_bop_yoy_m | "{C} Exports BoP" | M | %YoY (derive) |
| imports_bop_yoy_m | "{C} Imports BoP" | M | %YoY (derive) |
| exports_bop_usd_m / imports_bop_usd_m | "{C} Exports USD" / "Imports USD" | M | USD mn |
| cpi_yoy_m | "{C} Consumer Price Index" | M | %YoY (derive) |
| cpi_components | "{C} CPI by group" | M | index → contribution |
| policy_rate_m | "{C} Policy Rate" / "Central Bank Rate" | M | % |
| ppi_yoy_m | "{C} Producer Price Index" | M | %YoY (derive) |
| fx_usd_m | "{C} Exchange Rate per USD" | M | LCU/USD |
| unemployment_rate | "{C} Unemployment Rate" | M/Q | % |
| labor_force_part_rate | "{C} Labour Force Participation" | Q/A | % |
| real_wage | "{C} Real Wage" / "Average Wage" | Q/M | index/% |
| yield_10y / yield_2y | "{C} Government Bond Yield 10Y / 2Y" | M | % |
| consumer_confidence | "{C} Consumer Confidence" | M | index |
| stock_index_m | "{C} Stock Market Index" | D→M avg | index |

Notes:
- "%YoY (derive)" = fetch the index/level and compute 12-month (or 4-quarter)
  percentage change in the data-transformer step.
- Quarterly resampling uses `.resample('QE').mean()`; monthly stock index from
  daily uses `.resample('ME').mean()` (CLAUDE.md data standards).
- Keep everything **wide format** (date index, series as columns).

## GTA — trade tables (scripted, deterministic)

One command produces every export/import table and contribution series:
```
& '.\bin\python.ps1' '.claude/skills/country-report/scripts/gta_trade_tables.py' \
    --gta-code {CODE} --outdir output/data/country_report/{Country} --years 5
```
`{CODE}` is `config.gta_code` — the **2-letter** GTA reporter code (Indonesia=ID,
Vietnam=VN, Thailand=TH; GTA stores all ISO codes as 2 letters). Outputs (in that
outdir): `exports_top10_hs2.csv`, `exports_contrib_hs2.csv`,
`exports_contrib_hs2_full.csv`, the partner equivalents, and the `imports_*`
mirror. Contribution CSVs include a short `Group` (legend-friendly) plus
`Group_full`; tables/appendix should use the full name. The script anchors "last
year" to the latest **complete** 12-month year (e.g. 2025, not a partial 2026).
If it prints "No GTA rows", this country isn't in GTA — skip the GTA items, keep
the CEIC BOP charts.

## S&P Global Connect — PMI heatmap

Endpoint comes from `config.sp_pmi_endpoint` (user-supplied saved query, Monthly).
Fetch via the existing client, seasonally-adjusted rows only:
```
python src/api/sp_client.py "{endpoint}" --save --name "{Country} PMI"
```
Then read the seasonally-adjusted sub-indicators from `SP.db` and pivot to
month × indicator for the heatmap.

**Endpoint quirk (important):** users often give a `…/workbooks/<id>` URL (not a
`…/savedqueries/<id>` one). Workbooks endpoints **ignore pagination and return
the whole series in a single response**, with a different field schema
(`Concept`, `Geography`, `Industry`, `Seasonaladjustment` — not `Title`/
`EconomicConcept`/`Adjustment`). Because of that, `SPClient.fetch()`'s paging
loop will re-request page after page of the *same* rows forever. For a workbooks
URL, do a **single** `requests.get(url, auth=...)` (no pagination), build the
DataFrame yourself, filter `Seasonaladjustment` contains "Seasonally Adjusted",
and pivot `Date × Concept`. (Saved-query URLs work fine with the client as-is.)

If the endpoint is missing, ask the user once; if unavailable, skip section 8.

## Web research (qualitative-analyst)

- GDP narrative: `tradingeconomics.com/{te_slug}/gdp-growth-annual`
- Monetary stance: `tradingeconomics.com/{te_slug}/interest-rate`
- Fiscal policy: general search for the country's current/planned fiscal
  measures **with effective dates** (budget, subsidies, tax changes, stimulus).
Keep narrative tight and sourced; this is context around the data, not an essay.

## Charts — always viz-expert

Every chart in `report_structure.md` is produced by the **viz-expert** agent
(NESDC palette, FC Vision font) — never inline matplotlib. Hand viz-expert the
CSV path, chart type, title, the output PNG path under
`output/chart/country_report/{Country}/`, and any reference lines (target band,
long-run mean). Batch related charts in one delegation to save round-trips.

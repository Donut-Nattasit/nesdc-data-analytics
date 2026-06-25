# Country Economic Report — Canonical Structure

This is the skeleton every country report follows. It expands the user's draft
(`docs/country_economic_report/`) into an actionable build sheet: for each item,
the **source**, the **visual**, the **agent** that produces it, and the **output
file**. Build top to bottom, but honour the config `sections:` switches and the
**skip rule**.

## Skip rule (token discipline)
A country never has every series. After **2–3 genuine attempts** to locate a
series (CEIC search variants + a check that the config has no pinned ID), **skip
it and move on** — note the omission in one line rather than burning tokens
hunting. Whole sections can be disabled in `config.sections`. When you skip,
record it under a short "Data not available" note at the end of the affected
section so the reader knows it was deliberate.

## Numbering
Figures and tables are numbered sequentially **within the report**, restarting
at 1. Caption format (from CLAUDE.md):
- Figure: `**Figure N: Title**` immediately *below* the image.
- Table: `**Table N: Title**` immediately *above* the table.
- Source line: italic *Source: …, Year.* below the table (never a table row).
- Chart paths are relative: `../../output/chart/country_report/[country]/file.png`
  (report lives in `report/country_report/[country]/`).

## File naming
Charts → `output/chart/country_report/[country]/`, data → `output/data/country_report/[country]/`.
Use the `file:` names below verbatim so re-runs overwrite cleanly.

---

## 1. Executive Summary
Written **last**, synthesised from every section below. 4–8 sentences: growth
momentum, trade picture, inflation/policy stance, labour, and the single most
important risk or theme. No new data — only what the report already shows.

## 2. GDP

### 2.1 Overall growth
- **Latest quarterly real GDP growth (%YoY)** — CEIC. Vertical bar, data labels.
  `file: gdp_real_yoy_q.png` · viz-expert.
- **Narrative** — qualitative-analyst summarises
  `tradingeconomics.com/{te_slug}/gdp-growth-annual`.

### 2.2 Expenditure side
- **YoY growth by component** — CEIC. Table.
- **Share by component** — CEIC. Table.
- **Contribution to growth by component** — CEIC. Stacked bar.
  `file: gdp_contrib_expenditure.png`.

### 2.3 Production side
- **YoY growth by component** — CEIC. Table.
- **Share by component** — CEIC. Table.
- **Contribution to growth by component** — CEIC. Stacked bar.
  `file: gdp_contrib_production.png`.

### 2.4 Annual growth
- **Annual real GDP growth** — CEIC (or annualise quarterly). Vertical bar, labels.
  `file: gdp_real_annual.png`.

## 3. Foreign Trade
Run the bundled script once up front:
`scripts/gta_trade_tables.py --gta-code {gta_code} --outdir output/data/country_report/{country} --years 5`
(`gta_code` is the 2-letter GTA reporter code from config).
It emits every table/contribution CSV used below. If it warns "No GTA rows",
skip the GTA-sourced items but keep the CEIC BOP charts.

### 3.1 Exports
- **Monthly total exports, BOP basis (%YoY)** — CEIC. Vertical bar, labels.
  `file: exports_bop_yoy.png`.
- **Top 10 exports by HS2 (last year)** — `exports_top10_hs2.csv`. Table.
- **Contribution to growth of exports by HS2 (top 5 + Others)** —
  `exports_contrib_hs2.csv`. Stacked bar. `file: exports_contrib_hs2.png`.
  Footnote → Appendix full list.
- **Top 10 exports by partner country (last year)** — `exports_top10_partner.csv`. Table.
- **Contribution to growth of exports by country (top 5 + Others)** —
  `exports_contrib_partner.csv`. Stacked bar. `file: exports_contrib_partner.png`.

### 3.2 Imports
Mirror of 3.1 using the `imports_*` CSVs and `imports_bop_yoy.png`.

### 3.3 Trade balance
- **Monthly exports, imports & trade balance (USD)** — CEIC. Two stacked subplots:
  top = line chart of export & import values; bottom = vertical bar of the
  balance. `file: trade_balance.png`.

## 4. Fiscal Policy
- Fiscal measures being implemented or planned, **with effective dates** —
  qualitative-analyst web research. Prose + a small table if several measures.

## 5. Inflation, Exchange Rate & Monetary Policy

### 5.1 Consumer Price Index (CPI)
- **Monthly CPI %YoY** with a long-run average line and the central-bank target
  line/band — CEIC + `config.cpi_target`. Vertical bar. `file: cpi_yoy.png`.
- **Contribution to CPI growth by main group** — CEIC. Stacked bar.
  `file: cpi_contrib.png`.
- **Monthly policy rate** — CEIC. Line. `file: policy_rate.png`.
- **Monetary stance & latest decision** — qualitative-analyst summarises
  `tradingeconomics.com/{te_slug}/interest-rate`.

### 5.2 Producer Price Index (PPI)
- **PPI vs CPI %YoY** on one chart — CEIC. Line (two series). `file: ppi_vs_cpi.png`.

### 5.3 Exchange rate
- **Monthly average local currency per USD** with a horizontal long-run mean —
  CEIC. Line. `file: fx_usd.png`.

## 6. Labor Market
Data table of: unemployment rate, labour-force participation rate, real wage —
CEIC. Single table; add a small chart only if it adds insight.

## 7. Leading Indicators
Data table of: yield curve (10y − 2y or 10y − 3m spread), consumer confidence
index, stock-market performance (monthly average) — CEIC. Single table.

## 8. Purchasing Manager Indices (PMI)
- **Heatmap of monthly PMI sub-indicators**, seasonally-adjusted series only —
  S&P Global Connect via `config.sp_pmi_endpoint`. `file: pmi_heatmap.png`.
- The endpoint **must be supplied by the user**. If `config.sp_pmi_endpoint` is
  null, ask the user for it; if they don't have one, skip the section.

## 9. Country-unique sectors (`custom_sections`)
For each block in `config.custom_sections`, render a subsection (nested under
`placement` or standalone). Use the named `source`, `series`, and `chart`. This
is the mechanism that makes each country report bespoke — e.g. Indonesia
palm-oil exports, a commodity exporter's terms-of-trade, etc.

## 10. Appendix
- **Contribution to growth of exports & imports by HS2** — full sorted lists
  (`*_contrib_hs2_full.csv`), largest to smallest. Tables.
- **Contribution to growth of exports & imports by partner** — full sorted lists
  (`*_contrib_partner_full.csv`). Tables.

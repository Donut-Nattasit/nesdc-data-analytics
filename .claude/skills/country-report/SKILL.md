---
name: country-report
description: >
  Generates a comprehensive, config-driven country economic report (GDP, foreign
  trade, fiscal policy, inflation & monetary policy, labor market, leading
  indicators, and PMI) for any country, pulling from CEIC, GTA.db, S&P Global
  Connect, and web research. Each country has a reusable settings file so re-runs
  are fast and consistent, and country-unique sectors can be added. Use this
  whenever the user asks for a country economic report, a macro/economic brief or
  profile on a specific country (e.g. "economic report on Indonesia", "build a
  macro brief for Vietnam", "update the Indonesia country report"), or wants to
  add a country-specific sector to such a report — even if they don't say the word
  "report".
---

# Country Economic Report

## What this does
Builds a standardized-yet-flexible economic report for one country by assembling
data across CEIC (macro series), GTA.db (trade), S&P Global Connect (PMI), and
web research (fiscal/monetary narrative). The structure is fixed (so reports are
comparable across countries) but **every country has its own settings file** that
records resolved series IDs and lets you toggle sections or bolt on sectors that
exist only for that country. You are the orchestrator: delegate fetching,
charting, and writing to the workspace sub-agents.

## Operating principles
- **Config is memory.** The per-country `config.yaml` is the whole point of
  "repeatable". Resolve a series ID once, write it back to config, and every
  future run skips the search. Read config first; write discoveries back as you go.
- **Skip, don't grind.** No country has every series. After 2–3 honest attempts
  to find a series, skip it with a one-line note. Burning tokens hunting a series
  that doesn't exist is the main failure mode — avoid it. See the skip rule in
  `references/report_structure.md`.
- **Delegate everything specialized.** data-fetcher fetches, data-transformer
  cleans/derives growth rates, viz-expert makes **all** charts (mandatory — never
  inline matplotlib), qualitative-analyst does web narrative, report-writer
  assembles and can export HTML.
- **Stay wide format, English, Gregorian years** by default (CLAUDE.md). Thai only
  if explicitly requested.

## Reference files — read these as you need them
- `references/report_structure.md` — the canonical section-by-section build sheet
  (source, chart type, agent, output filename for every item). **Read this before
  building.**
- `references/data_recipes.md` — how to resolve/fetch each series (CEIC search
  keywords, GTA script, S&P, web). Read when fetching.
- `assets/config_template.yaml` — the per-country settings template.
- `scripts/gta_trade_tables.py` — bundled, deterministic GTA trade tables +
  contribution-to-growth (used for both exports and imports).

## Output locations (create up front)
For country `{C}`:
- Report + config → `report/country_report/{C}/`  (`report.md`, `config.yaml`)
- Charts → `output/chart/country_report/{C}/`
- Data → `output/data/country_report/{C}/`
Use the exact chart/data filenames from `report_structure.md` so re-runs overwrite.

## Execution protocol

### Step 1 — Resolve the config (memory)
1. If `report/country_report/{C}/config.yaml` exists, read it — this is a re-run;
   reuse pinned series IDs and section switches.
2. If not, copy `assets/config_template.yaml` there and fill `country`, `iso3`,
   `te_slug`. Create the three output directories.
3. Confirm with the user any **custom_sections** or section toggles they want for
   this country, and ask for the **S&P PMI endpoint** if `pmi` is on and
   `sp_pmi_endpoint` is null (there's no public search for it).

### Step 2 — Fetch & derive (per enabled section)
Walk `report_structure.md` top to bottom. For each enabled section:
- For CEIC items with a pinned `series_id`, fetch directly via data-fetcher.
  For null ones, search (see `data_recipes.md`), pick the best World Trend Plus
  match, fetch it, and **write the ID back into config.yaml**.
- Run `scripts/gta_trade_tables.py --iso3 {iso3} --outdir output/data/country_report/{C}`
  once to produce all trade tables.
- Have data-transformer derive %YoY where the source is an index/level, resample
  to the right frequency, and keep everything wide and saved to the data dir.
Apply the skip rule whenever a series can't be found.

### Step 3 — Charts (viz-expert, batched)
Hand viz-expert the CSVs, the chart type, titles, output PNG paths, and any
reference lines (CPI target band, long-run means). Batch related charts per
delegation. Every chart in `report_structure.md` is viz-expert's job — no
exceptions.

### Step 4 — Narrative (qualitative-analyst)
Get the GDP-growth narrative, the monetary stance, and the fiscal-policy measures
(with effective dates) from the sources in `data_recipes.md`. Keep it tight and
sourced.

### Step 5 — Assemble (report-writer)
Compile `report/country_report/{C}/report.md` following `report_structure.md`:
correct figure/table captions and numbering, relative chart paths
(`../../output/chart/country_report/{C}/...`), source citations, the appendix
full-contribution tables, and country `custom_sections` placed per their
`placement`. Write the **Executive Summary last**, synthesised from the finished
sections. Offer to export a self-contained HTML via the `export-html` skill.

### Step 6 — Report back
Tell the user what was built, which sections/series were **skipped** (and why),
and which series IDs got newly pinned into config for next time.

## Re-running / updating
On a later run, config.yaml already holds the pinned IDs — Step 1 becomes a quick
read, and the report refreshes fast. To add a country-unique sector, add a block
to `custom_sections` (see the template) and re-run; only that subsection changes.

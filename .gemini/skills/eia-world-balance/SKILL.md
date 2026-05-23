---
name: eia-world-balance
description: >
  One-command skill to refresh and re-render the EIA Short-Term Energy Outlook (STEO)
  World Petroleum Balance dual-subplot chart. Run this every time EIA publishes a new
  monthly STEO report to pull the latest production, consumption, and inventory data and
  regenerate both English and Thai localized visualizations.
---

# EIA World Petroleum Balance Skill

## Purpose

EIA publishes an updated **Short-Term Energy Outlook (STEO)** report every month. This skill:
1. Fetches the latest quarterly data for the three core world balance series from the EIA STEO API.
2. Filters to a user-configurable window (default: 2020-Q1 to 2027-Q4).
3. Saves a refreshed wide-format CSV to `output/data/transformed/`.
4. Re-renders both the **English** and **Thai** dual-subplot charts to `output/chart/`.

---

## Series Reference

| Series ID         | Name                                               | Unit  |
|-------------------|----------------------------------------------------|-------|
| `PAPR_WORLD`      | World Petroleum and Other Liquid Fuels Production  | mb/d  |
| `PATC_WORLD`      | World Petroleum, Other Liquid Fuels Consumption    | mb/d  |
| `T3_STCHANGE_WORLD` | Crude Oil & Liquids Inventory Net Withdrawals    | mb/d  |

---

## Chart Architecture

The dual-subplot layout is structured as follows:

```
┌─────────────────────────────────────────────────────────────────┐
│  [Figure Title]  EIA STEO: World Petroleum Balance             │
├─────────────────────────────────────────────────────────────────┤
│  [Top Subplot  — height ratio 2.2]                             │
│  World Petroleum Supply and Demand                             │
│  Line chart: PAPR_WORLD (navy) vs PATC_WORLD (red)             │
│  X-axis tick labels HIDDEN (shared via sharex)                 │
├─────────────────────────────────────────────────────────────────┤
│  [Bottom Subplot — height ratio 1.0]                           │
│  World Inventory Net Withdrawals                               │
│  Bar chart: T3_STCHANGE_WORLD                                  │
│   ├── Green  (#2f855a): Net Draws (positive values)            │
│   └── Grey   (#718096): Net Builds (negative values)           │
│  X-axis ticks: Q1 and Q3 of each year, rotated 35°            │
└─────────────────────────────────────────────────────────────────┘
```

**Key layout rules:**
- `sharex=True` ensures both subplots are perfectly date-aligned.
- Top X-axis tick labels are suppressed (`visible=False`); only the bottom shows ticks.
- Both X-axis title labels are hidden (`label.set_visible(False)`) to eliminate whitespace.
- `hspace=0.12` keeps the two subplots tightly coupled.
- A `zero reference line` (`axhline`) is drawn in the bottom subplot.

---

## Execution Protocol

### Step 1 — Check Freshness (Cache-First)
Before running, check `.gemini/PROJECT_STATE.md` for the last update date of:
- `output/data/transformed/eia_world_balance_quarterly.csv`

If the **Last Update** is **less than 1 month old**, the cache is still fresh. Ask the user if they want to force a refresh.
If EIA has published a new STEO since the last update (typically the 2nd week of each month), **always force refresh** using `force_refresh=True`.

### Step 2 — Run the Pipeline Script

Execute the self-contained runner script from the project root using the **Python Execution Standard**:

```powershell
$env:PYTHONPATH='.'; .\.venv\Scripts\python.exe src/visualization/generate_eia_balance_report.py
```

This script automatically:
- Fetches fresh quarterly STEO data (with `force_refresh=True` hardcoded for monthly update runs).
- Filters to the display window (2020-Q1 → end of STEO forecast horizon).
- Saves the refreshed wide-format CSV to `output/data/transformed/eia_world_balance_quarterly.csv`.
- Renders and saves the English chart: `output/chart/eia_world_balance_quarterly.png`.
- Renders and saves the Thai chart: `output/chart/eia_world_balance_quarterly_thai.png`.

### Step 3 — Update the Project State Registry
After successful execution, update `.gemini/PROJECT_STATE.md`:
- Set the **Last Update** timestamp for both chart rows to today's date.
- Update the **Data Range** field if EIA has extended the STEO forecast horizon.

---

## Configuration Options

When invoking this skill, you may override these defaults:

| Parameter       | Default            | Description                                              |
|-----------------|--------------------|----------------------------------------------------------|
| `start_date`    | `'2020-01-01'`     | Start of the display window (YYYY-MM-DD, Q1 of the year) |
| `end_date`      | `'2027-12-31'`     | End of the display window (extend as EIA horizon grows)  |
| `force_refresh` | `True` for updates | Whether to bypass cache and pull latest STEO from API   |
| `thai_locale`   | Both rendered      | Pass `True` for Thai only, `False` for English only     |

To change the display window, edit the `main()` function in [generate_eia_balance_report.py](file:///C:/Users/natta/OneDrive%20-%20nesdc.go.th/NESDC/Gemini/data-analysis/src/visualization/generate_eia_balance_report.py).

---

## Output Artifacts

| Artifact                                        | Description                                    |
|-------------------------------------------------|------------------------------------------------|
| `output/data/transformed/eia_world_balance_quarterly.csv` | Wide-format quarterly data (Supply, Demand, Stock Change) |
| `output/chart/eia_world_balance_quarterly.png`  | English dual-subplot chart                     |
| `output/chart/eia_world_balance_quarterly_thai.png` | Thai localized dual-subplot chart (B.E. ticks) |

---

## Monthly Refresh Checklist

When EIA publishes a new STEO report, follow this checklist:

- `[ ]` Confirm the EIA STEO release date (typically the 2nd Tuesday of each month).
- `[ ]` Run the pipeline with `force_refresh=True` to pull the latest API data.
- `[ ]` Verify the new chart covers the updated forecast horizon (EIA typically extends by 1 month each release).
- `[ ]` Confirm that the last bar in the stock changes subplot reflects the latest STEO projection.
- `[ ]` Update `PROJECT_STATE.md` with the new Last Update date and data range.

---

## Troubleshooting

| Issue | Resolution |
|-------|-----------|
| `EIA_API_KEY` not found | Check `.env` file at project root; key must be set as `EIA_API_KEY=<your_key>` |
| Empty DataFrame returned | Confirm series IDs are uppercase: `PAPR_WORLD`, `PATC_WORLD`, `T3_STCHANGE_WORLD` |
| Font warning for `FC Vision` | Ensure `assets/fonts/FCVision/` contains `FCVision-Regular.ttf` and `FCVision-Bold.ttf` |
| Thai characters not rendering | `FC Vision` supports Thai; if garbled, check that font files are registered in `configure_matplotlib_font()` |
| Chart X-axis misaligned | Do not use separate `ax.set_xlim()` calls — `sharex=True` handles alignment automatically |

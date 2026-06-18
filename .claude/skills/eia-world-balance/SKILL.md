---
name: eia-world-balance
description: >
  Executes a monthly refresh and visual rendering of the EIA Short-Term Energy Outlook (STEO) World Petroleum Balance. Use when the EIA publishes a new STEO report.
---

# EIA World Petroleum Balance Skill

## Purpose
EIA publishes an updated Short-Term Energy Outlook (STEO) report every month. This skill automates the retrieval of quarterly production, consumption, and inventory withdrawal data, computes wide-format matrices, and renders localized dual-subplot visualizations.

## Decision Tree: Refresh Logic
When executing the EIA update, follow this conditional pipeline flow:

```
                      Is there a new monthly STEO released?
                                         │
                  ┌──────────────────────┴──────────────────────┐
                  ▼ (Yes)                                       ▼ (No)
          [Force Refresh = True]                  Is local cache <30 days old?
                  │                                             │
                  │                                     ┌───────┴───────┐
                  ▼                                     ▼ (Yes)         ▼ (No)
         [Fetch EIA API]                         [Load Cache CSV]  [Force Refresh = True]
                  │                                     │               │
                  ▼                                     ▼               ▼
        [Save database/CSV]                      [Render Charts]  [Fetch EIA API]
```

## Execution Protocol

### Step 1 — Verify Cache
* Check the modification date of `output/data/transformed/eia_world_balance_quarterly.csv` to determine when the pipeline last ran.
* If a new STEO has been published since the last run (typically the 2nd week of each month), proceed to Step 2 with `force_refresh=True`.

### Step 2 — Run the Black-Box Script
* Run the pipeline script from the root directory using the standard environment template:
  ```powershell
  $env:PYTHONPATH='.'; .\.venv\Scripts\python.exe src/visualization/generate_eia_balance_report.py
  ```
* The script automatically handles API fetches, filters, and renders both English (`output/chart/eia_world_balance_quarterly.png`) and Thai (`output/chart/eia_world_balance_quarterly_thai.png`) visual charts.

## Troubleshooting

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| `EIA_API_KEY not found` | Environment key missing in `.env` | Add `EIA_API_KEY=<key>` to the root `.env` file. |
| `Font warning for FC Vision` | Matplotlib cannot locate custom font files | Ensure `assets/fonts/FCVision/` contains the necessary `.ttf` files and clear the matplotlib font cache. |
| `X-axis mismatch in subplots` | Separate `xlim` definitions overriding `sharex` | Ensure `sharex=True` is set on the subplot grid and avoid calling manual limits on individual axes. |

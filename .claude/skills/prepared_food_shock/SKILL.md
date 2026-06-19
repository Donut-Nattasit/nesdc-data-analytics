---
name: prepared-food-shock
description: >
  Runs the Prepared Food CPI geopolitical price shock scenario analysis (Iran War Scenario). Calibrates non-linear price transmission using a 1.5x Dampened Scaling factor from the 2022 Russia-Ukraine shock, re-aggregates composites, generates comparison charts, and outputs a dedicated special economic brief.
---

# Prepared Food CPI Price Shock Scenario Analysis Skill

## Purpose
This skill executes the geopolitical price shock scenario pipeline for domestic food inflation in Thailand. It simulates the impact of a sharp oil price spike (such as the March 2026 Iran war oil shock to $128.78/bbl) on the Prepared Food CPI index and propagates the shock to Headline and Core inflation. It outputs comparison datasets, charts, and a standalone research report.

## Decision Tree: Calibration and Scaling Flow
Use this tree to configure the simulation scaling and execution flow:

```
                            Determine Oil Spike Event
                     (e.g., March 2026 Iran War: $128.78/bbl)
                                         │
                                         ▼
                            Compute Relative Shock Size
                   (Compare against 2022 Russia-Ukraine Spike: $110.89)
                                         │
                                         ▼
                             Select Scaling Multiplier
                   ┌─────────────────────┼─────────────────────┐
                   ▼ (Linear Scaling)    ▼ (Dampened - Recommended) ▼ (Equal Magnitude)
                 Multiplier = 2.7x     Multiplier = 1.5x      Multiplier = 1.0x
                   │                     │                     │
                   └─────────────────────┼─────────────────────┘
                                         ▼
                               [Run Pipeline Script]
                          (Simulation -> Aggregate -> Chart)
                                         │
                                         ▼
                             Compile Reports & Registry
                       (Embed base64 images & convert HTML)
```

## Execution Protocol

### Step 1 — Check Baseline Data Freshness
* The simulation uses the baseline CPI forecast as its input. Verify that `output/data/cpi_forecast/cpi_forecast_monthly.csv` is populated with the latest baseline run. If not, execute the `cpi-forecast` skill first.

### Step 2 — Run the Pipeline
* Run the entire simulation, chart generation, and report building pipeline using the PowerShell runner script from the project root:
  ```powershell
  .\src\pipeline\prepared_food_shock\run_pipeline.ps1
  ```
* Alternatively, execute the two Python scripts sequentially:
  ```powershell
  # Step 2a: Run simulation and plot charts
  $env:PYTHONPATH='.'; $env:PYTHONUTF8='1'; .\bin\python.ps1 src/pipeline/prepared_food_shock/run_analysis.py

  # Step 2b: Generate Markdown scenario brief and register
  $env:PYTHONPATH='.'; $env:PYTHONUTF8='1'; .\bin\python.ps1 src/pipeline/prepared_food_shock/generate_report.py
  ```

### Step 3 — Export Portable HTML Report (Optional but Recommended)
* To export the report as a portable, self-contained HTML file (with base64 embedded charts for email distribution), execute the conversion skill script:
  ```powershell
  $env:PYTHONPATH='.'; .\bin\python.ps1 .agents/skills/md-to-html/scripts/md_to_html.py report/prepared_food_shock/prepared_food_shock.md report/prepared_food_shock/prepared_food_shock.html
  ```

### Step 4 — Verification
* Verify that comparison charts and datasets are saved to `output/chart/prepared_food_shock/` and `output/data/prepared_food_shock/`.

## Troubleshooting

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| `[FAIL] Baseline monthly forecast not found` | The baseline CPI forecasting pipeline has not been executed | Execute the `cpi-forecast` skill first to establish the baseline dataset. |
| `SyntaxError: invalid syntax (LaTeX equations)` | Escaping issues in report template string | Do not use f-strings to write LaTeX equations with curly braces. Write reports as normal raw strings and use `.replace()` for placeholders (e.g. `{{TABLE_1}}`). |
| `MathJax LaTeX equations display raw code` | MathJax CDN blocked or offline | Open the HTML file in a web browser connected to the internet. On first load, MathJax files will download and cache locally. |

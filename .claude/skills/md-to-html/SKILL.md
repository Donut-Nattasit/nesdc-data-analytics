---
name: md-to-html
description: >
  Converts Markdown reports to single, portable, self-contained HTML files with base64-embedded images and MathJax LaTeX math rendering. Use when exporting reports for sharing or email distribution.
---

# Markdown to HTML Export Skill

## Purpose
This skill converts standard markdown reports into portable HTML documents. It embeds all local image assets as base64 data URIs and integrates MathJax v3 for offline/online mathematical equation rendering, resolving broken links in emails or shares.

## Decision Tree: Export Output Selection
Use this logic to define input and output paths for the conversion:

```
                            Is the report project-specific?
                                         │
                  ┌──────────────────────┴──────────────────────┐
                  ▼ (Yes)                                       ▼ (No)
     Input: report/[project_name]/[file].md           Input: report/[file].md
     Output: report/[project_name]/[file].html        Output: report/[file].html
                  │                                             │
                  └──────────────────────┬──────────────────────┘
                                         ▼
                            Run Black-Box Python Script
                        (Embeds base64 charts & MathJax CDN)
```

## Execution Protocol

### Step 1 — Check Dependencies
* Run the validation snippet to ensure the required python libraries (`markdown`, `pymdown-extensions`) are installed:
  ```powershell
  $env:PYTHONPATH='.'; .\bin\python.ps1 -c "import markdown; import pymdownx; print('Dependencies OK')"
  ```
* If this command fails, install them:
  ```powershell
  $env:PYTHONPATH='.'; .\bin\python.ps1 -m pip install markdown pymdown-extensions
  ```

### Step 2 — Execute the Conversion
* Call the python converter script with the input and output arguments using the relative environment template:
  ```powershell
  $env:PYTHONPATH='.'; .\bin\python.ps1 .agents/skills/md-to-html/scripts/md_to_html.py <INPUT_MD_PATH> <OUTPUT_HTML_PATH>
  ```
  *Example*:
  ```powershell
  $env:PYTHONPATH='.'; .\bin\python.ps1 .agents/skills/md-to-html/scripts/md_to_html.py report/energy_price_forecast/energy_price_forecast.md report/energy_price_forecast/energy_price_forecast.html
  ```

### Step 3 — Post-Flight Verification
* Verify that the generated HTML has base64 data strings instead of relative paths for all visual figures, ensuring it is self-contained.

## Troubleshooting

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: markdown` | Dependencies not installed in the active virtual environment | Run the pip install commands specified in Step 1. |
| `Warning: Image path not found` | Chart image does not exist at the relative path specified in markdown | Verify that the chart PNG exists in `output/chart/` and is referenced correctly relative to the project root. |
| `Math equations display raw LaTeX code` | MathJax CDN blocked or offline | Open the HTML file in a browser with active internet connection. On first load, MathJax resources are cached locally. |

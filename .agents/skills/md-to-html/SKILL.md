---
name: md-to-html
description: Converts any Markdown report to a portable, self-contained HTML file with base64-embedded images and MathJax math rendering. Invoke this skill whenever the user asks to export, share, or email a .md report as HTML.
---

# Skill: Markdown → Self-Contained HTML Export

## When to Invoke This Skill

Trigger this skill automatically when the user says any of the following (or similar intent):
- "export to HTML", "convert to HTML", "make it self-contained"
- "email the report", "share the report"
- "export .md to .html", "HTML version of the report"

The `@report_writer` agent MUST invoke this skill as the final step after writing any `.md` report, if the user requests an HTML export.

## What the Skill Does

Runs `scripts/md_to_html.py` (inside this skill folder) to produce a **single `.html` file** that:

- **Embeds all chart images as base64** — no relative paths, no broken images when emailed.
- **Renders LaTeX math** (`$...$` and `$$...$$`) via MathJax v3 CDN — opens in any browser.
- **Includes clean professional CSS** — paper-style layout, styled tables and headings.
- **Strips YAML front-matter** — the `---` header block is removed from the HTML output.

## Execution Steps

### Step 1 — Identify paths

| Variable | Value |
|---|---|
| `<INPUT_MD>` | Relative path to the source Markdown file (e.g., `report/my_report.md`) |
| `<OUTPUT_HTML>` | Same path but with `.html` extension (e.g., `report/my_report.html`) |

### Step 2 — Run the converter

Execute from the **workspace root** using the standard Python execution protocol:

```powershell
$env:PYTHONPATH='.'; .\.venv\Scripts\python.exe .agents/skills/md-to-html/scripts/md_to_html.py <INPUT_MD> <OUTPUT_HTML>
```

**Example** for `report/Thailand_HHI_Market_Concentration_2566.md`:

```powershell
$env:PYTHONPATH='.'; .\.venv\Scripts\python.exe .agents/skills/md-to-html/scripts/md_to_html.py report/Thailand_HHI_Market_Concentration_2566.md report/Thailand_HHI_Market_Concentration_2566.html
```

### Step 3 — Verify & Report

After running, confirm to the user:
- The output `.html` file path
- File size in KB
- Number of images embedded
- Whether MathJax is included

### Step 4 — Advise the user

Always close with this advisory note:

> **Email tip**: Attach the `.html` file directly. Your recipient opens it in any browser — no Python, no missing images. MathJax math renders on first open (requires internet); subsequent opens are cached for offline use.

## Error Handling

| Problem | Action |
|---|---|
| Image not found (WARN in output) | Report which image path was missing; check `output/chart/` folder exists |
| `ModuleNotFoundError: markdown` | Run `.\.venv\Scripts\python.exe -m pip install markdown pymdown-extensions` first |
| Unicode/encoding errors | The script always writes UTF-8; ensure the `.html` is opened as UTF-8 in the email client |

## Dependency Check

Before first run, verify packages are installed:

```powershell
$env:PYTHONPATH='.'; .\.venv\Scripts\python.exe -c "import markdown; import pymdownx; print('Dependencies OK')"
```

If the check fails, install:

```powershell
$env:PYTHONPATH='.'; .\.venv\Scripts\python.exe -m pip install markdown pymdown-extensions
```

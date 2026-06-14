---
trigger: always_on
glob: "*"
description: Enforce Python execution protocols, zero absolute paths, chart relative pathing, and localization rules.
---

# Code & Reporting Protocols

## 1. Zero Absolute Paths (Mandatory)
* Never hardcode absolute paths (e.g., `C:\Users\natta\...`). This workspace syncs dynamically across different machine architectures and usernames.
* Always resolve file paths dynamically relative to the project root. In Python, utilize `pathlib.Path.cwd()` or `pathlib.Path(__file__).parent` references.

## 2. Python Execution Protocol
To avoid module import conflicts and guarantee the local virtual environment dependencies are used correctly, execute all Python processes using the following template:
* **Interpreter Path**: `.\.venv\Scripts\python.exe` (relative from workspace root).
* **Python Path**: Set the environment variable `PYTHONPATH` to `.` (the current directory).
* **Unified PowerShell Template**:
  ```powershell
  $env:PYTHONPATH='.'; $env:PYTHONUTF8='1'; .\.venv\Scripts\python.exe path/to/script.py
  ```
  *(Do NOT wrap the execution in a nested `powershell -Command "..."` string because the workspace shell is already PowerShell. Doing so causes variable expansion and quote escaping errors like parser and terminator failures.)*

## 3. Relative Pathing for Charts in Reports
* When referencing charts under `output/chart/` from Markdown reports, always use correct relative pathing (Markdown compilers require this to render previews):
  * For general reports under `report/` (e.g., `report/some_brief.md`), use: `![Chart Caption](../output/chart/filename.png)`
  * For project-specific reports under subdirectories (e.g., `report/dubai_oil/some_report.md`), use: `![Chart Caption](../../output/chart/filename.png)`

## 4. Localization Standards
* **Default Language**: Use English for all reports, charts, datasets, and Gregorian calendar years (YYYY).
* **Thai Localization**: Only use the `TH Sarabun New` font, Buddhist Era (B.E.) calendar standards, and Thai language utilities in `src/visualization/` if the user explicitly requests "Thai localization" or "Thai language".
* **Thai Reporting Model Recommendation**: When the user requests a report to be written in Thai, you should gently remind the user that they can manually switch the model to **Claude 3.5 Sonnet** in their IDE settings, as it performs significantly better at Thai language generation. This is optional; if the user prefers to proceed with the current model, you may generate the Thai text as requested.

## 5. File Renaming & Path Integrity
* Every time the user makes any changes to files or folder names, you MUST search for them and make sure changes do not break any path, especially for charts embedded in reports.

## 6. Report Formatting — Figure & Table Captions (Mandatory)
* **`@report_writer` MUST apply sequential captions to every figure and every table in all reports without exception.**
* **Charts / Figures**: Embed every chart image with a bold caption immediately below it in the format:
  ```
  ![Alt text](../output/chart/filename.png)
  **Figure [N]: [Descriptive title of the chart]**
  ```
* **Tables**: Precede every Markdown table with a bold caption in the format:
  ```
  **Table [N]: [Descriptive title of the table]**
  | Col A | Col B |
  |-------|-------|
  ```
* **Numbering**: Figures and Tables are numbered in **two independent sequences** (Figure 1, Figure 2 … and Table 1, Table 2 …), both restarting from 1 in each report document.
* **No Exceptions**: This rule applies to every report format — pipeline reports, research briefs, model summaries, and ad-hoc outputs alike.

## 7. Table Source Citations — External Placement (Mandatory)
* **Never** embed the data source as a row inside a table (e.g., a merged `| Source: ... |` last row). Doing so forces an abnormally tall final row and breaks table aesthetics.
* **Always** place the source attribution **outside and immediately below** the table as a small italic note, using the format:
  ```
  *Source: [Organisation / Database name], [Year or date range].*
  ```
* This rule applies equally to Markdown (`.md`) and HTML (`.html`) reports.

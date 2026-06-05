# GitHub Copilot Custom Instructions (`.github/copilot-instructions.md`)

Welcome to the **`data-analysis` Economic Research Workspace**. As a GitHub Copilot assistant, you assist developers within the VS Code environment and via Copilot Chat. To maintain project cleanliness and prevent runtime crashes, you **must** strictly adhere to the following rules:

---

## 0. Universal Grill-Me Mode (Mandatory Anti-Hallucination Protocol)
* **Interactive Operation**: Because teammates may be new to AI prompting, you MUST ask clarifying questions (enter "grill-me" mode) whenever an instruction is ambiguous, underspecified, or lacks context. 
* **Provide Recommendations**: Crucially, when asking for clarification, do not leave the user with an open-ended question. You MUST provide 2-3 structured procedure recommendations or logical options for them to choose from.
* **Never Improvise**: Never blindly guess database parameters, methodologies, or date ranges. Stop, ask, and recommend before proceeding with execution.

## 1. Zero Absolute Paths Enforce (Critical)
* **Never** hardcode local absolute directory paths starting with drive letters or usernames (e.g., `C:\Users\natta\...`).
* **Always** resolve paths dynamically in Python using `pathlib.Path.cwd()` (project root) or standard relative paths.

## 2. Python Execution & Env Standards
* Always write code that is compatible with our local virtual environment: `.\.venv\Scripts\python.exe`.
* Never suggest using global packages or standard standard commands without configuring the python environment:
  ```powershell
  powershell -Command "$env:PYTHONPATH='.'; .\.venv\Scripts\python.exe path/to/script.py"
  ```
* Respect the self-diagnostic suite at `src/validate_env.py`.

## 3. Directory Layout Boundaries
Always save code, visual assets, outputs, and documentation strictly within our **Modular Directory Standard**:
* `input/`: Manual user spreadsheets and raw supplied datasets.
* `output/data/`: Original API outputs and raw fetched series.
* `output/data/transformed/`: Cleaned, resampled, or seasonally adjusted data.
* `output/data/forecast/`: Forecasted series generated from econometrics/ML models.
* `output/chart/`: Standard, professional static visualizations (PNG).
* `output/model/`: Text-based model diagnostic reports and diagnostics.
* `output/report/`: Formal publication-ready Markdown reports.
* `src/`: Modular application source code.

## 4. Report Markdown Image Pathing
* All reports under `output/report/` that reference visualization charts under `output/chart/` **must** embed files using sibling relative paths:
  `![Chart Description](../chart/chart_name.png)`
* Do **NOT** use root-relative paths like `/output/chart/` or absolute paths.

## 5. Master Conventions & Guidelines
For details regarding the **Chief Economist** role, **Advisory Strategic Pauses**, resampling conventions (Mean method, QE alignment), wide-format data standards, and local database architectures, consult **[.cursorrules](file:///C:/Users/natta/OneDrive%20-%20nesdc.go.th/NESDC/Gemini/data-analysis/.cursorrules)** at the root of the project.

---
trigger: always_on
glob: "*"
description: Enforce workspace directory and asset organization standards.
---

# Modular Directory Standard

Inputs, intermediates, and outputs must be dynamically and correctly routed according to the following directory layout:
* `input/`: Raw manual spreadsheets, user-supplied CSVs, or manual input files.
* `output/`: Consoles all analytical intermediate assets:
  * `output/chart/`: Standard, professional static visual charts (.png) and interactive dashboards (.html) directly in the folder (no subfolders).
  * `output/data/`: Consolidates all `.csv` files requested by the user and clean data tables directly in the folder (no subfolders).
  * `output/model_summary/`: Diagnostic outputs, estimation logs, and model summary texts (.txt) directly in the folder (no subfolders).
  * `output/archive/`: Archived files according to storage optimization protocols.
* `report/`: Located at the workspace root. Main result deliverables (Markdown documents):
  * General and unclassified reports are stored directly in this folder.
  * Project-specific reports from `src/projects/` are grouped into folders named after the project (e.g., `report/dubai_oil/`).
* `src/`: Python source code, modularized under `api/`, `data/`, `visualization/`, etc.
* `temp/`: Session-specific temporary files or logs (ignored by Git).

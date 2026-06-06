---
trigger: always_on
glob: "report/**/*.md"
description: Use correct relative pathing when embedding charts in reports.
---

# Relative Pathing for Charts in Reports

* When referencing charts under `output/chart/` from Markdown reports:
  * For general reports under `report/` (e.g., `report/some_brief.md`), use:
    `![Chart Caption](../output/chart/filename.png)`
  * For project-specific reports under subdirectories (e.g., `report/dubai_oil/some_report.md`), use:
    `../../output/chart/filename.png`
* Do not use absolute paths or root-relative paths. Correct relative paths are required for Markdown compilers and previews to render images correctly.

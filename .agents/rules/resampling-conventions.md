---
trigger: always_on
glob: "src/data/**/*.py"
description: Use Mean method and Quarter-End ('QE') alignment when resampling time-series to quarterly frequency.
---

# Resampling & Aggregation Conventions

* **Frequency Conversions**: When resampling time-series data to a quarterly frequency, apply:
  * **Method**: **Mean** (Average of observations).
  * **Temporal Alignment**: **Quarter-End ('QE')** (e.g., `2026-03-31`, `2026-06-30`).

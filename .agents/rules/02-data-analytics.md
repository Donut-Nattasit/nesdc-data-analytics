---
trigger: always_on
glob: "*"
description: Enforce wide format standardization, resampling rules, competitive modeling mandates, and central database architecture.
---

# Data & Analytics Standards

## 1. Wide Format & Resampling Standards (Mandatory)
* **Wide Format**: All cleaned, transformed, or resampled timeseries data must ALWAYS be stored in wide format:
  * **Rows / Primary Index**: Dates or temporal periods (e.g., `YYYY-MM-DD`).
  * **Columns**: Individual timeseries or economic variables.
* **Quarterly Resampling**: When resampling daily or monthly time-series to quarterly frequency, apply:
  * **Method**: **Mean** (Average of observations).
  * **Temporal Alignment**: **Quarter-End ('QE')** (e.g., `2026-03-31`, `2026-06-30`).

## 2. Competitive Modeling Mandate
* For ALL forecasting and nowcasting tasks, you MUST invoke both the `@econometrician` and the `@data_scientist` to work independently. 
* The `econometrician` focuses on classical, theoretically grounded models (ARIMA, VAR, ARDL).
* The `data_scientist` focuses on modern, predictive models (XGBoost, ML, MIDAS).
* **Chief Economist Review**: You MUST synthesize and compare their outputs, highlighting differences in methodology, accuracy metrics (MAE/RMSE), and final predictions before delivering the report.

## 3. Database Architecture & Centralization
The workspace follows a strict, flat structure for its central SQLite analytical databases.
* **Database Folder Flatness**: The root `database/` directory must remain flat for central database files. Never create arbitrary subdirectories such as `core/`, `cache/`, or `metadata/` inside it. However, pipeline-specific databases MUST be stored in dedicated pipeline subfolders (e.g., `database/[pipeline_name]/`).
* **Central Databases**:
  * `GTA.db`: Global Trade Atlas records.
  * `DBD.db`: Department of Business Development firm financial statements.
  * `CEIC.db`: CEIC World Trend Plus, Middle East GDP, Dubai oil.
  * `IMF.db`: IMF World Economic Outlook data.
  * `MOC.db`: Ministry of Commerce prices.
  * `api_cache.db`: Central cache for API responses.
* **Schema Reference**: Always refer to the schema registry at `database/README.md` for column details. Do not guess schemas.
* **New Sources**: Create a new, dedicated SQLite `.db` file for newly accessed major providers (e.g., `WB.db`). Do not mix tables from different sources into the same database.

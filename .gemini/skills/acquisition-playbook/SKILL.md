---
name: acquisition-playbook
description: Master playbook for global API and database retrieval. Consolidates CEIC, BOT, EIA, PortWatch, and SQL database search heuristics, pagination logic, and formatting standards.
---

# Acquisition Playbook

This is the unified data retrieval playbook. It provides specific strategies for querying the various economic databases within our workspace.

## 1. Unified Retrieval Standards
* **SQLite Storage Mandatory**: Do not save loose `.csv` files by default. Save all fetched time-series data to the consolidated SQLite database at `output/data/time_series.db` using the `sqlite3` library or pandas `to_sql()`. Only dump a CSV if explicitly requested by the user during the Grill-Me phase.
* **Wide Format Mandatory**: If fetching multiple series, pivot them into wide format (Index = Date, Columns = Series) before inserting into the database.
* **Temporary Scripting**: Always generate API requests as temporary scripts in `temp/` using standard `PYTHONPATH` conventions. Delete them immediately after execution.
* **Pagination**: Use optimized endpoints that automatically paginate (e.g. EIA STEO multi-series endpoints) to avoid hitting loop ceilings.

## 2. Database Specific Heuristics

### CEIC Database
* **Database Priorities**: Favor World Trend Plus (GEM) first for global requests.
* **Search Refinement**: If search returns noisy "Trade Partner" data, append exclusionary keywords. Refer to `references/search-heuristics.md` for advanced CEIC parameters.

### Bank of Thailand (BOT) & EIA
* **Batch Fetching**: Use list inputs for IDs wherever the client allows (especially EIA STEO). See `references/api_patterns.md` for code snippets.

### Global Trade Atlas (GTA)
* **SQL Query Execution**: Connect directly to `database/GTA.db`. Always filter by `Flow` and `Year` to prevent double-counting of import/export aggregates.

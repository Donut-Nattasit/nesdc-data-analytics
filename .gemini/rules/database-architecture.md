# Database Architecture Standard

The workspace follows a strict, flat structure for its databases and registry to maintain clarity and avoid deep folder nesting.

* **Registry Location**: The central project manifest (`PROJECT_STATE.json`) MUST be located at the root of the workspace. It is the single source of truth for datasets, models, visualizations, and reports. All agents and scripts must use `src/utils/registry.py` to interact with it.
* **Database Folder Strict Flatness**: The `database/` directory must remain completely flat. It is exclusively for raw SQLite `.db` files (e.g., `GTA.db`, `CEIC.db`, `IMF.db`, `MOC.db`, `DBD.db`) and the schema `README.md`.
* **No Subfolders**: Never create subdirectories such as `core/`, `cache/`, or `metadata/` inside the `database/` folder. All relational schemas and documentation are centralized in `database/README.md`.
* **API Cache**: The API cache database must also reside directly in `database/api_cache.db`.

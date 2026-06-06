---
trigger: always_on
glob: "*"
description: Enforce central SQLite database path conventions and schema reference guidelines.
---

# Central Databases Standard

The workspace contains central SQLite analytical databases. When writing queries or interacting with databases:
* **GTA Database**: Located at `./database/GTA.db`. Contains Global Trade Atlas records, import/export series, and transaction details.
* **DBD Database**: Located at `./database/DBD.db`. Contains Department of Business Development firm financial statements and TSIC sector mapping.
* **CEIC Database**: Located at `./database/CEIC.db`. Contains CEIC World Trend Plus indicators, Middle East GDP series, and Dubai oil prices.
* **IMF Database**: Located at `./database/IMF.db`. Contains IMF World Economic Outlook growth, inflation, and policy rate series.
* **MOC Database**: Located at `./database/MOC.db`. Contains Ministry of Commerce retail and wholesale prices.
* **API Cache**: Located at `./database/api_cache.db`. Central cache for API responses.
* **Schema Reference**: Always refer to the database schema registry at [database/README.md](file:///c:/Users/natta/OneDrive%20-%20nesdc.go.th/NESDC/MyAI/data-analysis/database/README.md) for table columns, index descriptions, and query optimization details. Do not guess schemas.

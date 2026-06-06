# 🗄️ Workspace Database Schema Registry

This file documents the structures, tables, and columns of the central SQLite databases in the workspace. Any AI or developer can use these schemas to write precise, high-fidelity SQL queries.

## 📁 Directory Structure Overview

The `./database/` folder is organized as follows:
*   **`GTA.db`**: Global Trade Atlas database (HS2 meta, ISO meta, and transaction series).
*   **`DBD.db`**: Department of Business Development database (TSIC sector hierarchies and firm financial statements).
*   **`IMF.db`**: International Monetary Fund database (World GDP growth, Thailand inflation, ASEAN-4 GDP growth).
*   **`CEIC.db`**: CEIC database (World Trend Plus metadata and series, Middle East GDP growth, Dubai oil prices).
*   **`MOC.db`**: Ministry of Commerce database (Thailand product prices).
*   **`api_cache.db`**: API client query cache (caching responses from IMF, MOC, BOT, World Bank, EIA).
*   **`data_dict/`**: Directory for static reference metadata and data dictionaries (formerly `metadata/`).
*   **`README.md`**: This entry point schema registry.

---

## 📁 Database: `GTA.db`
* **Workspace Path**: `./database/GTA.db`

### 📋 Table: `meta_hs2`
| CID | Column Name | Type | Primary Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| 0 | **HS2_Code** | `INTEGER` | | HS 2-Digit Chapter Code |
| 1 | **HS2_Desc_EN** | `TEXT` | | HS2 Description in English |
| 2 | **HS2_Desc_TH** | `TEXT` | | HS2 Description in Thai |

### 📋 Table: `meta_iso`
| CID | Column Name | Type | Primary Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| 0 | **ISO** | `TEXT` | | ISO 3-Letter Country Code |
| 1 | **Name_EN** | `TEXT` | | Country Name in English |
| 2 | **Name_TH** | `TEXT` | | Country Name in Thai |
| 3 | **Region** | `TEXT` | | Geographic Region |

### 📋 Table: `GTA`
| CID | Column Name | Type | Primary Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| 0 | **Year** | `INTEGER` | | Transaction Year |
| 1 | **Month** | `INTEGER` | | Transaction Month |
| 2 | **Trade_Direction** | `TEXT` | | Direction (Import/Export) |
| 3 | **Reporter_ISO** | `TEXT` | | Reporter Country ISO Code |
| 4 | **Partner_ISO** | `TEXT` | | Partner Country ISO Code |
| 5 | **HS2_Code** | `INTEGER` | | HS 2-Digit Chapter Code |
| 6 | **USD** | `REAL` | | Trade Value in USD |

---

## 📁 Database: `DBD.db`
* **Workspace Path**: `./database/DBD.db`
Contains TSIC industry structure mappings and financial reports of Thai firms.

### 📋 Table: `financial_statements`
Contains details of assets, liabilities, revenues, and profits of registered Thai firms grouped by TSIC industry codes.

---

## 📁 Database: `CEIC.db`
* **Workspace Path**: `./database/CEIC.db`

### 📋 Table: `metadata` (CEIC World Trend Plus Metadata)
| CID | Column Name | Type | Primary Key |
| :--- | :--- | :--- | :--- |
| 0 | **series_id** | `TEXT` | 🔑 PRIMARY KEY |
| 1 | **series_name** | `TEXT` | |
| 2 | **country** | `TEXT` | |
| 3 | **frequency** | `TEXT` | |
| 4 | **units** | `TEXT` | |
| 5 | **last_updated** | `TEXT` | |
| 6 | **description** | `TEXT` | |

### 📋 Table: `series_data` (CEIC World Trend Plus Series values)
| CID | Column Name | Type | Primary Key |
| :--- | :--- | :--- | :--- |
| 0 | **series_id** | `TEXT` | 🔑 PRIMARY KEY |
| 1 | **date** | `TEXT` | 🔑 PRIMARY KEY |
| 2 | **value** | `REAL` | |

### 📋 Table: `middle_east_gdp_yoy` (Middle East country real GDP growth YoY)
Wide format layout resampled to Quarter-End ('QE'). Columns map to country names (e.g. `Saudi Arabia`, `United Arab Emirates`, `Egypt`, etc.).

### 📋 Table: `ceic_dubai_oil_price` (Historical Dubai Oil Prices)
Contains historical price records fetched from CEIC database.

---

## 📁 Database: `IMF.db`
* **Workspace Path**: `./database/IMF.db`
Contains macroeconomic series fetched via IMF WEO/CPI APIs.

### 📋 Table: `thailand_inflation`
Thailand annual consumer price inflation (YoY % change) spanning 2015 to 2031 (forecast).

### 📋 Table: `world_gdp_growth`
World real GDP annual output growth (YoY % change) spanning 2015 to 2031 (forecast).

### 📋 Table: `asean_gdp_growth`
Real GDP growth (YoY % change) resampled at annual periods for Thailand, Indonesia, Malaysia, and Philippines spanning 2018 to 2031.

---

## 📁 Database: `MOC.db`
* **Workspace Path**: `./database/MOC.db`
Contains price data from Ministry of Commerce.

### 📋 Table: `moc_product_prices_wide`
Daily product price series compiled in wide format (Columns are product IDs, rows are dates).

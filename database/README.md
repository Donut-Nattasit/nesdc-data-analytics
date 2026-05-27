# 🗄️ Workspace Database Schema Registry

This file documents the structures, tables, and columns of the central SQLite databases in the workspace. Any AI or developer can use these schemas to write precise, high-fidelity SQL queries.

## 📁 Directory Structure Overview

The `./database/` folder is organized as follows:
*   **`core/`**: Houses permanent SQLite databases used for analysis and charting (`GTA.db`, `World_Trend_Plus.db`, `time_series.db`).
*   **`cache/`**: Contains transient/temporary SQLite cache buffers (`api_cache.db`).
*   **`metadata/`**: Contains static reference metadata files (`moc_product_metadata.csv`).
*   **`README.md`**: This entry point schema registry.

---

## 📁 Database: `GTA.db`
* **Workspace Path**: `./database/core/GTA.db`

### 📋 Table: `meta_hs2`
* **Record Count**: 99 rows

| CID | Column Name | Type | Not Null | Default Value | Primary Key |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | **HS2_Code** | `INTEGER` | ❌ | NULL |  |
| 1 | **HS2_Desc_EN** | `TEXT` | ❌ | NULL |  |
| 2 | **HS2_Desc_TH** | `TEXT` | ❌ | NULL |  |

### 📋 Table: `meta_iso`
* **Record Count**: 211 rows

| CID | Column Name | Type | Not Null | Default Value | Primary Key |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | **ISO** | `TEXT` | ❌ | NULL |  |
| 1 | **Name_EN** | `TEXT` | ❌ | NULL |  |
| 2 | **Name_TH** | `TEXT` | ❌ | NULL |  |
| 3 | **Region** | `TEXT` | ❌ | NULL |  |

### 📋 Table: `GTA`
* **Record Count**: 29,773,024 rows

| CID | Column Name | Type | Not Null | Default Value | Primary Key |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | **Year** | `INTEGER` | ❌ | NULL |  |
| 1 | **Month** | `INTEGER` | ❌ | NULL |  |
| 2 | **Trade_Direction** | `TEXT` | ❌ | NULL |  |
| 3 | **Reporter_ISO** | `TEXT` | ❌ | NULL |  |
| 4 | **Partner_ISO** | `TEXT` | ❌ | NULL |  |
| 5 | **HS2_Code** | `INTEGER` | ❌ | NULL |  |
| 6 | **USD** | `REAL` | ❌ | NULL |  |

---

## 📁 Database: `World_Trend_Plus.db`
* **Workspace Path**: `./database/core/World_Trend_Plus.db`

### 📋 Table: `metadata`
* **Record Count**: 106 rows

| CID | Column Name | Type | Not Null | Default Value | Primary Key |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | **series_id** | `TEXT` | ❌ | NULL | 🔑 PRIMARY KEY |
| 1 | **series_name** | `TEXT` | ❌ | NULL |  |
| 2 | **country** | `TEXT` | ❌ | NULL |  |
| 3 | **frequency** | `TEXT` | ❌ | NULL |  |
| 4 | **units** | `TEXT` | ❌ | NULL |  |
| 5 | **last_updated** | `TEXT` | ❌ | NULL |  |
| 6 | **description** | `TEXT` | ❌ | NULL |  |

### 📋 Table: `series_data`
* **Record Count**: 12,760 rows

| CID | Column Name | Type | Not Null | Default Value | Primary Key |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | **series_id** | `TEXT` | ❌ | NULL | 🔑 PRIMARY KEY |
| 1 | **date** | `TEXT` | ❌ | NULL | 🔑 PRIMARY KEY |
| 2 | **value** | `REAL` | ❌ | NULL |  |

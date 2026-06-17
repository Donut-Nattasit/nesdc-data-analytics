# 🗄️ Workspace Database Schema Registry

This file documents the structures, tables, and columns of the central SQLite databases in the workspace. Any AI or developer can use these schemas to write precise, high-fidelity SQL queries.

## 📁 Directory Structure Overview

The `./database/` folder is organized as follows:
*   **`GTA.db`**: Global Trade Atlas database (HS2 meta, ISO meta, and transaction series).
*   **`DBD.db`**: Department of Business Development database (firm financial statements).
*   **`IMF.db`**: International Monetary Fund database (World GDP growth, Thailand inflation, ASEAN-4 GDP growth).
*   **`CEIC.db`**: CEIC database (World Trend Plus metadata and series, Middle East GDP growth, Dubai oil prices).
*   **`MOC.db`**: Ministry of Commerce database (Thailand product prices and product metadata).
*   **`WB.db`**: World Bank database (global development indicators and macroeconomic metadata).
*   **`TSIC.db`**: Thailand Standard Industrial Classification database (TSIC sector hierarchies and descriptions).
*   **`api_cache.db`**: Central cache for API responses.
*   **`energy_price_forecast/energy_price_forecast.db`**: SQLite database cache specific to the energy price forecast pipeline.
*   **`ex_im_price_forecast/ex_im_price_forecast.db`**: SQLite database cache specific to the export and import price forecast pipeline.
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
### 📋 Table: `moc_product_prices_wide`
Daily product price series compiled in wide format (Columns are product IDs, rows are dates).

### 📋 Table: `moc_product_metadata`
| CID | Column Name | Type | Primary Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| 0 | **product_id** | `TEXT` | 🔑 PRIMARY KEY | Product ID code (e.g. P11009) |
| 1 | **product_name_th** | `TEXT` | | Product Name in Thai |
| 2 | **category** | `TEXT` | | Product Category |
| 3 | **sale_type** | `TEXT` | | Product Sale Type (e.g. Retail) |

---

## 📁 Database: `WB.db`
* **Workspace Path**: `./database/WB.db`
Contains macroeconomic indicators and global development metadata fetched via the World Bank API.

### 📋 Table: `indicators_metadata`
| CID | Column Name | Type | Primary Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| 0 | **indicator_id** | `TEXT` | 🔑 PRIMARY KEY | World Bank indicator ID |
| 1 | **name** | `TEXT` | | Indicator full name |
| 2 | **description** | `TEXT` | | Detailed description of the indicator |

### 📋 Table: `series_data`
| CID | Column Name | Type | Primary Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| 0 | **indicator_id** | `TEXT` | 🔑 PRIMARY KEY | World Bank indicator ID |
| 1 | **iso3c** | `TEXT` | 🔑 PRIMARY KEY | Country ISO3 Code |
| 2 | **date** | `TEXT` | 🔑 PRIMARY KEY | Date / Year of the observation |
| 3 | **value** | `REAL` | | Indicator value |

---

## 📁 Database: `TSIC.db`
* **Workspace Path**: `./database/TSIC.db`
Contains Thailand Standard Industrial Classification (TSIC) sector hierarchy and descriptions.

### 📋 Table: `tsic_mapping`
| CID | Column Name | Type | Primary Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| 0 | **หมวดใหญ่** | `TEXT` | | Category letter (A-U) |
| 1 | **หมวดย่อย** | `TEXT` | | 2-digit division code |
| 2 | **หมู่ใหญ่** | `TEXT` | | 3-digit group code |
| 3 | **หมู่ย่อย** | `TEXT` | | 4-digit class code |
| 4 | **กิจกรรม** | `TEXT` | | 5-digit activity code |

### 📋 Table: `tsic_category`
| CID | Column Name | Type | Primary Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| 0 | **หมวดใหญ่** | `TEXT` | | Category letter (A-U) |
| 1 | **คำอธิบาย** | `TEXT` | | Description in Thai |
| 2 | **Description** | `TEXT` | | Description in English |

### 📋 Table: `tsic_division`
| CID | Column Name | Type | Primary Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| 0 | **หมวดย่อย** | `TEXT` | | 2-digit division code |
| 1 | **คำอธิบาย** | `TEXT` | | Description in Thai |
| 2 | **Description** | `TEXT` | | Description in English |

### 📋 Table: `tsic_group`
| CID | Column Name | Type | Primary Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| 0 | **หมู่ใหญ่** | `TEXT` | | 3-digit group code |
| 1 | **คำอธิบาย** | `TEXT` | | Description in Thai |
| 2 | **Description** | `TEXT` | | Description in English |

### 📋 Table: `tsic_class`
| CID | Column Name | Type | Primary Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| 0 | **หมู่ย่อย** | `TEXT` | | 4-digit class code |
| 1 | **คำอธิบาย** | `TEXT` | | Description in Thai |
| 2 | **Description** | `TEXT` | | Description in English |

### 📋 Table: `tsic_activity`
| CID | Column Name | Type | Primary Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| 0 | **กิจกรรม** | `TEXT` | | 5-digit activity code |
| 1 | **คำอธิบาย** | `TEXT` | | Description in Thai |
| 2 | **Description** | `TEXT` | | Description in English |

---

## 📁 Pipeline Database: `energy_price_forecast/energy_price_forecast.db`
* **Workspace Path**: `./database/energy_price_forecast/energy_price_forecast.db`
Contains local cached datasets specifically for the energy price forecasting pipeline (fetched from the U.S. EIA STEO API).

### 📋 Table: `api_cache`
Follows the standard cache table schema.

---

## 📁 Pipeline Database: `ex_im_price_forecast/ex_im_price_forecast.db`
* **Workspace Path**: `./database/ex_im_price_forecast/ex_im_price_forecast.db`
Contains local cached datasets specifically for the export and import price index forecasting pipeline (fetched from the BOT API).

### 📋 Table: `api_cache`
Follows the standard cache table schema.

---

## 📁 Database: `LFS.db`
* **Workspace Path**: `./database/LFS.db`
Contains the Labor Force Survey (LFS) database with over 22 million survey records and standard reference classification codebooks.

### 📋 Table: `lfs_data`
Contains individual survey response microdata. Key columns include:
| Column Name | Type | Description |
| :--- | :--- | :--- |
| **year_gregorian** | `INTEGER` | Gregorian Calendar Year (e.g. 2025) |
| **quarter** | `INTEGER` | Quarter (1, 2, 3, 4) |
| **area** | `INTEGER` | Area Code (1 = Municipal, 2 = Non-Municipal) |
| **cwt** | `TEXT` | Province code (cwt), matching `lfs_province_codes.code` |
| **age** | `INTEGER` | Age of individual |
| **age_01** | `INTEGER` | Raw age input from 2025 survey |
| **occup** | `TEXT` | Occupation code (ISCO) |
| **indus_group** | `TEXT` | Industry code (ISIC) |
| **grade_a** | `TEXT` | Educational level completed code |
| **grade_b** | `TEXT` | Educational subject/type code |
| **weight** | `REAL` | Expansion weight |

### 📋 Table: `lfs_province_codes`
| Column Name | Type | Description |
| :--- | :--- | :--- |
| **code** | `TEXT` | 2-digit Province code |
| **name_th** | `TEXT` | Province name in Thai |
| **name_en** | `TEXT` | Province name in English |

### 📋 Table: `lfs_metadata_columns`
Metadata dictionary mapping database columns to human-readable names and descriptions.

### 📋 Table: `lfs_occupation_codes`
| Column Name | Type | Description |
| :--- | :--- | :--- |
| **code** | `TEXT` | 1-digit category or 2-digit division occupation code |
| **name_th** | `TEXT` | Occupation name in Thai |
| **level** | `INTEGER` | Classification level (1 = Major Group, 2 = Sub-Major Group) |

### 📋 Table: `lfs_industry_codes`
| Column Name | Type | Description |
| :--- | :--- | :--- |
| **code** | `TEXT` | 1-letter category (A-Q) or 2-digit division industry code |
| **name_th** | `TEXT` | Industry name in Thai |
| **level** | `INTEGER` | Classification level (1 = Category, 2 = Division) |

### 📋 Table: `lfs_education_recodes`
Maps original survey education codes to the recoded target classification.
| Column Name | Type | Description |
| :--- | :--- | :--- |
| **original_grade_a** | `TEXT` | Original education level completed (F8 / grade_a) |
| **original_grade_b** | `TEXT` | Original education subject/type (F10 / grade_b), or `NULL` if matches all subjects |
| **recode_code** | `TEXT` | Recoded educational classification code (01 to 20) |
| **recode_name** | `TEXT` | Recoded educational name in Thai |

### 📋 Table: `lfs_education_recode_labels`
| Column Name | Type | Description |
| :--- | :--- | :--- |
| **recode_code** | `TEXT` | Primary key recode code |
| **recode_name** | `TEXT` | Recoded educational classification name in Thai |



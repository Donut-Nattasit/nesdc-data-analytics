# Project State Registry (MANIFEST)

This file tracks the current state of analytical assets in the workspace. Agents MUST update this file upon successful completion of a task.

## 1. Datasets (`output/data/`)
| Series ID | Source | Raw Path (`output/data/raw/`) | Transformed Path (`output/data/transformed/`) | Forecast Path (`output/data/forecast/`) | Status | Last Update |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dubai Oil Scenarios** | **Excel (User Input)** | **input/oil_price_scenarios.xlsx** | **output/data/transformed/oil_price_scenarios.csv** | | **Ready** | 2026-05-13 |
| WTIPUUS, BREPUUS | EIA STEO | output/data/raw/eia_crude_oil_prices.csv | | | Ready | 2026-05-13 |
| Aggregate ImPI (Q) | User | input/ImPI_q.csv | output/data/transformed/ExPI_q.csv | | Ready | 2026-05-10 |
| Local Project Database | SQLite | output/data/database/World_Trend_Plus.db | | | Ready | 2026-05-10 |
| 541395757, 352376202, 352376302, 367523747 | CEIC | output/data/raw/th_prices_raw.csv | | | Ready | 2026-05-15 |
| **Quarterly Price Master** | **Mixed** | **output/data/raw/th_prices_raw.csv** | **output/data/transformed/th_prices_quarterly_for_deflator.csv** | **output/data/forecast/th_prices_scenarios_forecast.csv** | **Ready** | 2026-05-15 |
| Global Trade Atlas (GTA) | GTA | input/GTA/combined.csv | output/data/database/GTA.db | | Ready | 2026-05-01 |
| International Crude Oil Production | EIA (v2) | output/data/raw/eia_crude_oil_production_monthly.csv | output/data/transformed/petroleum_production_grouped.csv | | Ready | 2026-05-12 |
| EC_XT_046_S2 (9 Series) | BOT | output/data/raw/bot_EC_XT_046_S2_*.csv | | | Ready | 2025-05-22 |
| 317092601 | CEIC | output/data/raw/ceic_317092601.csv | | | Ready | 2026-05-22 |
| 413247317 | CEIC | output/data/raw/ceic_413247317.csv | | | Ready | 2026-05-22 |
| **GDP Backtest Train** | **Consolidated** | **Multiple** | **output/data/transformed/gdp_backtest_train.csv** | | **Ready** | 2026-05-23 |
| GDP Backtest Validation | Consolidated | Multiple | output/data/transformed/gdp_backtest_validation.csv | | Ready | 2026-05-23 |
| **Strait of Hormuz Transits** | **IMF PortWatch** | **output/data/raw/hormuz_transits.csv** | | | **Ready** | 2026-05-16 |
| **HS85 Exports to USA** | **GTA (SQLite)** | **output/data/raw/hs85_exports_to_usa.csv** | **output/data/transformed/hs85_exports_to_usa_ma_yoy.csv** | | **Ready** | 2026-05-17 |
| **HS85 Exports to World** | **GTA (SQLite)** | **output/data/raw/hs85_exports_to_world.csv** | **output/data/transformed/hs85_exports_to_world_ma_yoy.csv** | | **Ready** | 2026-05-17 |
| **Labor Nationwide (M)** | **BOT (EC_RL_009_S4)** | **output/data/raw/bot_labor_nationwide_monthly.csv** | | | **Ready** | 2026-05-24 |
| **Thai Real GDP Growth** | **CEIC / Fallback** | **output/data/raw/thailand_gdp_cvm.csv** | **output/data/transformed/thailand_gdp_growth.csv** | | **Ready** | 2026-05-20 |
| **NIEs Monthly Exports** | **CEIC (4 Series)** | **output/data/raw/nies_exports_raw.csv** | output/data/transformed/nies_exports_growth_yoy.csv | | **Ready** | 2026-05-20 |
| **Thailand Top 5 Exports** | **GTA (SQLite)** | **output/data/raw/thailand_top5_exports_raw.csv** | **output/data/transformed/thailand_top5_exports_growth.csv** | | **Ready** | 2026-05-20 |



## 2. Models (`output/model/`)
| Model Name | Type | Data Source | Summary Path | Status |
| :--- | :--- | :--- | :--- | :--- |
| TH Public Debt ARIMA | Auto-ARIMA | output/data/raw/ceic_th_public_debt_gdp.csv | output/model/th_public_debt_gdp_arima_summary.txt | Finalized |
| US Inflation ARDL | ARDL | output/data/raw/us_inflation_m2_ardl_data.csv | output/model/us_inflation_m2_ardl_summary.txt | Finalized |
| US Macro VAR | VAR | output/data/raw/us_macro_var_transformed.csv | output/model/us_macro_var_summary.txt | Finalized |
| US Macro Causality | Granger | output/data/raw/us_macro_var_transformed.csv | output/model/us_macro_var_causality.txt | Finalized |
| US Real GDP ARIMA | Auto-ARIMA | output/data/raw/us_real_gdp_historical.csv | output/model/us_real_gdp_arima_summary.txt | Finalized |

## 3. Visualizations (`output/chart/`)
| Chart Name | Type | Source Data | PNG Path | Status |
| :--- | :--- | :--- | :--- | :--- |
| Global Petroleum Production | Stacked Bar | output/data/transformed/petroleum_production_grouped.csv | output/chart/global_petroleum_production_stacked.png | Rendered |
| ASEAN GDP YoY | Line | output/data/transformed/asean_gdp_yoy_transformed.csv | output/chart/asean_gdp_yoy_q1_2026.png | Rendered |
| ASEAN Exports YoY | Line | output/data/raw/asean_exports_raw.csv | output/chart/asean_exports_yoy.png | Rendered |
| Thailand GDP Contribution | Bar/Stacked | output/data/raw/thailand_gdp_components_cvm.csv | output/chart/thailand_gdp_contribution_final_local_font.png | Rendered |
| Thailand Inflation Contribution | Bar/Stacked | output/data/raw/thailand_inflation_contribution.csv | output/chart/thailand_inflation_contribution_labeled.png | Rendered |
| Thailand Public Debt | Line | output/data/raw/ceic_th_public_debt_gdp.csv | output/chart/thailand_public_debt_gdp.png | Rendered |
| Oil Prices Forecast | Line | output/data/forecast/oil_prices_forecast_full.csv | output/chart/oil_prices_full_forecast.png | Rendered |
| US Real GDP Forecast | Line | output/data/forecast/us_real_gdp_forecast.csv | output/chart/us_real_gdp_forecast.png | Rendered |
| India Exports YoY (Bar) | Bar | output/data/raw/india_exports_yoy.csv | output/chart/india_exports_yoy_bar.png | Rendered |
| THB/USD Monthly | Line | output/data/raw/bop_summary_usd.csv | output/chart/thb_usd_monthly_avg_final.png | Rendered |
| China GDP & Export YoY | Line (Stacked) | output/data/transformed/china_gdp_export_yoy.csv | output/chart/china_gdp_export_yoy.png | Rendered |
| India Exports Component Growth | Horizontal Bar | March 2026 Sectoral Data | output/chart/india_exports_components_mar2026.png | Rendered |
| **Thailand Real GDP Growth YoY** | **Line** | **output/data/transformed/thailand_gdp_growth.csv** | **output/chart/thailand_gdp_growth_yoy.png** | **Rendered** |
| **NIEs Exports YoY Growth** | **Line** | **output/data/transformed/nies_exports_growth_yoy.csv** | **output/chart/nies_exports_growth_yoy.png** | **Rendered** |
| **Thailand Top 5 Exports YoY Comparison** | **Grouped Bar** | **output/data/transformed/thailand_top5_exports_growth.csv** | **output/chart/thailand_top5_exports_comparison.png** | **Rendered** |



## 4. Formal Reports (`output/report/`)
| Report Title | Author | Date | Path | Status |
| :--- | :--- | :--- | :--- | :--- |
| ASEAN Q1 2026 News Context | news_analyst | 2026-05-10 | output/report/news_context_asean_q1_2026.md | Published |
| ASEAN Economic Performance Report: Q1 2026 | report_writer | 2026-05-10 | output/report/ASEAN_GDP_Q1_2026_Final.md | Published |
| Analysis of India's Export Performance: March 2026 | report_writer | 2026-04-15 | output/report/India_Export_Decline_Mar2026.md | Published |
| India Export Decline: March 2026 (Data-Driven Update) | report_writer | 2026-04-16 | output/report/India_Export_Decline_Mar2026_DataDriven.md | Published |
| **Thailand Real GDP Growth Analysis** | **report_writer** | **2026-05-20** | **output/report/Thailand_Real_GDP_Growth_Analysis.md** | **Published** |
| **NIEs Exports YoY Growth Analysis** | **report_writer** | **2026-05-20** | **output/report/NIEs_Exports_Growth_YoY_Analysis.md** | **Published** |
| **Thailand Top 5 Exports Analysis** | **report_writer** | **2026-05-20** | **output/report/Thailand_Top5_Exports_Analysis_2025_2026.md** | **Published** |
| **Thailand Rubber Q1 2026 News Context** | **news_analyst** | **2026-05-20** | **output/report/news_context_rubber_2026.md** | **Published** |


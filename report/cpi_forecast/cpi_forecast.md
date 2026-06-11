# Thailand CPI Forecasting Report

> **Pipeline**: `cpi_forecast` | **Forecast Horizon**: June 2026 – December 2027  
> **Source**: CEIC API (Thailand NSO CPI Data) | **Model**: auto-ARIMA / ARIMAX  
> **Generated**: 11 June 2026

---

## Executive Summary

As of **May 2026**, Thailand's Headline CPI index stands at **103.44** (2023 = 100),
with a year-on-year growth rate of **+2.89%**.

The NESDC auto-ARIMA model projects Headline CPI growth to **recover to 1.88%** in 2026,
driven primarily by a temporary rebound in energy prices, before moderating to **0.59%** in 2027.
Core inflation is expected to remain subdued, staying within the 0.9–1.0% band over the forecast horizon.

**Table 1: Annual CPI YoY Growth — Historical (2021–2025) & Forecast (2026–2027)**

|   date |   Headline (%) |   Core (%) |   Raw Food (%) |   Energy (%) |
|-------:|---------------:|-----------:|---------------:|-------------:|
|   2021 |           1.09 |       0.27 |          -1.24 |        10.78 |
|   2022 |           5.84 |       3.05 |           6.46 |        22.79 |
|   2023 |           1.28 |       1.30 |           2.60 |        -0.51 |
|   2024 |           0.44 |       0.55 |           0.26 |         0.10 |
|   2025 |          -0.05 |       0.79 |          -0.63 |        -4.14 |
|   2026 |           1.88 |       0.89 |           0.36 |         9.33 |
|   2027 |           0.59 |       1.03 |           1.53 |        -2.31 |

![Thailand CPI Annual Growth Bar Chart](../../output/chart/cpi_forecast/chart_exec_annual_growth_bar.png)
**Figure 1: Annual YoY Growth Rate by CPI Aggregate — Historical and Forecast**

---

## 1. CPI Overview

### 1.1 Monthly CPI Index Level

The following charts show the historical monthly CPI index levels for each composite
(2021–latest actual). All indices are rebased to 2023 = 100.

![CPI Monthly Index Level](../../output/chart/cpi_forecast/chart_overview_index_level.png)
**Figure 2: Thailand CPI Monthly Index Level by Composite (2021–Latest Actual, 2023 = 100)**

### 1.2 Monthly YoY Growth

![CPI Monthly YoY Growth](../../output/chart/cpi_forecast/chart_overview_yoy_growth.png)
**Figure 3: Thailand CPI Monthly Year-on-Year Growth (%) by Composite (2021–Latest Actual)**

---

### 1.3 CPI Weight Composition

The pie chart below shows the share of each composite group in the total CPI basket,
based on the most recent available weights (as of **May 2026**).

![CPI Weight Pie Chart](../../output/chart/cpi_forecast/chart_weight_pie.png)
**Figure 4: CPI Weight Composition — Core, Raw Food, and Energy (Latest Month)**

**Table 2: CPI Component Weights — Sorted by Share (Latest Month)**

|    | Component                             |   Weight | Group    |
|---:|:--------------------------------------|---------:|:---------|
|  0 | Housing Furnishing ex Utility         |    19.46 | Core     |
|  1 | Prepared Food                         |    16.65 | Core     |
|  2 | Transport Communication ex Motor Fuel |    14.41 | Core     |
|  3 | Transport Communication Motor Fuel    |     9.53 | Energy   |
|  4 | Meats Poultry Fish                    |     7.02 | Raw Food |
|  5 | Medical Personal Care                 |     6.12 | Core     |
|  6 | Vegetables Fruits                     |     4.79 | Raw Food |
|  7 | Housing Furnishing Utility            |     4.46 | Energy   |
|  8 | Recreation Reading Education Religion |     3.96 | Core     |
|  9 | Rice Flour Cereal                     |     3.40 | Raw Food |
| 10 | Non Alcoholic Beverages               |     3.30 | Core     |
| 11 | Apparel Footwears                     |     2.02 | Core     |
| 12 | Eggs Dairy Products                   |     1.70 | Raw Food |
| 13 | Tobacco Alcoholic Beverages           |     1.21 | Core     |
| 14 | Seasoning Condiments                  |     1.14 | Core     |
| 15 | Sugar Product                         |     0.84 | Core     |

---

### 1.4 Contribution to Growth

The following charts decompose the Headline CPI's YoY growth into contributions from
each composite group and individual component.

![Contribution to Growth — Composite](../../output/chart/cpi_forecast/chart_contribution_composite.png)
**Figure 5: Contribution to Headline CPI YoY Growth by Group (Core / Raw Food / Energy)**

![Contribution to Growth — Component](../../output/chart/cpi_forecast/chart_contribution_component.png)
**Figure 6: Contribution to Headline CPI YoY Growth by Individual Component**

---

## 2. CPI Forecasting

### 2.1 Monthly Forecast

The component-level monthly forecast charts are provided in **Appendix B**.
The charts below focus on the composite-level monthly forecast.

![Monthly Forecast — Composite YoY](../../output/chart/cpi_forecast/chart_forecast_monthly_composite_yoy.png)
**Figure 7: Monthly CPI YoY Growth Forecast — Headline, Core, Raw Food, Energy (Jan 2026–Dec 2027)**

**Table 3: Monthly CPI YoY Growth Forecast (Jan 2026–Dec 2027)**

| date     |   Headline (%) |   Core (%) |   Raw Food (%) |   Energy (%) |
|:---------|---------------:|-----------:|---------------:|-------------:|
| Jan 2026 |          -0.60 |       0.48 |          -0.00 |        -8.02 |
| Feb 2026 |          -0.79 |       0.42 |          -1.12 |        -7.89 |
| Mar 2026 |          -0.04 |       0.53 |          -0.74 |        -2.49 |
| Apr 2026 |           3.02 |       0.57 |           0.00 |        20.47 |
| May 2026 |           2.89 |       0.70 |          -0.38 |        19.38 |
| Jun 2026 |           2.66 |       0.89 |          -0.66 |        16.96 |
| Jul 2026 |           2.66 |       1.03 |           0.55 |        14.64 |
| Aug 2026 |           2.65 |       1.05 |           1.67 |        13.10 |
| Sep 2026 |           2.64 |       1.19 |           1.69 |        12.29 |
| Oct 2026 |           2.73 |       1.26 |           2.07 |        12.46 |
| Nov 2026 |           2.46 |       1.21 |           1.22 |        11.88 |
| Dec 2026 |           2.24 |       1.31 |           0.06 |        11.44 |
| Jan 2027 |           2.49 |       1.33 |           1.09 |        12.17 |
| Feb 2027 |           2.68 |       1.28 |           2.39 |        12.37 |
| Mar 2027 |           2.14 |       1.37 |           1.54 |         7.60 |
| Apr 2027 |          -0.49 |       1.32 |           1.06 |       -10.03 |
| May 2027 |          -0.49 |       1.06 |           1.69 |        -9.66 |
| Jun 2027 |          -0.29 |       0.98 |           1.79 |        -8.31 |
| Jul 2027 |          -0.10 |       0.93 |           1.55 |        -6.73 |
| Aug 2027 |           0.07 |       0.88 |           1.37 |        -5.21 |
| Sep 2027 |           0.21 |       0.85 |           1.42 |        -4.17 |
| Oct 2027 |           0.23 |       0.82 |           1.39 |        -3.96 |
| Nov 2027 |           0.35 |       0.80 |           1.48 |        -3.16 |
| Dec 2027 |           0.49 |       0.78 |           1.58 |        -2.22 |

---

### 2.2 Quarterly Forecast

![Quarterly Forecast — Composite YoY](../../output/chart/cpi_forecast/chart_forecast_quarterly_composite_yoy.png)
**Figure 8: Quarterly CPI YoY Growth Forecast — Composite Aggregates (2026–2027)**

**Table 4: Quarterly CPI YoY Growth Forecast (2026–2027)**

|         |   Headline (%) |   Core (%) |   Raw Food (%) |   Energy (%) |
|:--------|---------------:|-----------:|---------------:|-------------:|
| Q1 2026 |          -0.48 |       0.48 |          -0.62 |        -6.16 |
| Q2 2026 |           2.86 |       0.72 |          -0.35 |        18.93 |
| Q3 2026 |           2.65 |       1.09 |           1.30 |        13.35 |
| Q4 2026 |           2.48 |       1.26 |           1.11 |        11.93 |
| Q1 2027 |           2.44 |       1.33 |           1.67 |        10.67 |
| Q2 2027 |          -0.42 |       1.12 |           1.51 |        -9.34 |
| Q3 2027 |           0.06 |       0.89 |           1.44 |        -5.38 |
| Q4 2027 |           0.35 |       0.80 |           1.48 |        -3.12 |

---

### 2.3 Annual Forecast

![Annual Forecast — Composite YoY](../../output/chart/cpi_forecast/chart_forecast_annual_composite_yoy.png)
**Figure 9: Annual CPI YoY Growth — Historical and Forecast (2021–2027)**

**Table 5: Annual CPI YoY Growth — Historical and Forecast (2021–2027)**

|   date |   Headline (%) |   Core (%) |   Raw Food (%) |   Energy (%) |
|-------:|---------------:|-----------:|---------------:|-------------:|
|   2021 |           1.09 |       0.27 |          -1.24 |        10.78 |
|   2022 |           5.84 |       3.05 |           6.46 |        22.79 |
|   2023 |           1.28 |       1.30 |           2.60 |        -0.51 |
|   2024 |           0.44 |       0.55 |           0.26 |         0.10 |
|   2025 |          -0.05 |       0.79 |          -0.63 |        -4.14 |
|   2026 |           1.88 |       0.89 |           0.36 |         9.33 |
|   2027 |           0.59 |       1.03 |           1.53 |        -2.31 |

---

## Appendix

### Appendix A: CPI Weight Changes Over Time

![Weight Area — Composite](../../output/chart/cpi_forecast/chart_appendix_weight_area_composite.png)
**Figure 10: 100% Area Chart — CPI Weight by Composite Group Over Time**

![Weight Area — Component](../../output/chart/cpi_forecast/chart_appendix_weight_area_component.png)
**Figure 11: 100% Area Chart — CPI Weight by Individual Component Over Time**

---

### Appendix B: CPI and Growth by Component

![Component Level](../../output/chart/cpi_forecast/chart_appendix_component_level.png)
**Figure 12: Monthly CPI Index Level by Component (2021–Forecast, dashed line = forecast)**

![Component YoY](../../output/chart/cpi_forecast/chart_appendix_component_yoy.png)
**Figure 13: YoY Growth (%) by Individual CPI Component — Monthly (2021–Forecast)**

**Table 6: Monthly Component YoY Growth (%) — Jan 2026 to Dec 2027**

| date     |   Rice Flour Cereal |   Meats Poultry Fish |   Eggs Dairy Products |   Vegetables Fruits |   Seasoning Condiments |   Non Alcoholic Beverages |   Sugar Product |   Prepared Food |   Apparel Footwears |   Housing Furnishing ex Utility |   Housing Furnishing Utility |   Medical Personal Care |   Transport Communication ex Motor Fuel |   Transport Communication Motor Fuel |   Recreation Reading Education Religion |   Tobacco Alcoholic Beverages |
|:---------|--------------------:|---------------------:|----------------------:|--------------------:|-----------------------:|--------------------------:|----------------:|----------------:|--------------------:|--------------------------------:|-----------------------------:|------------------------:|----------------------------------------:|-------------------------------------:|----------------------------------------:|------------------------------:|
| Jan 2026 |               -0.40 |                 0.72 |                 -1.73 |               -0.11 |                  -1.75 |                      2.49 |            0.85 |            1.73 |               -1.69 |                           -0.15 |                        -4.67 |                   -1.32 |                                    0.53 |                               -10.13 |                                    0.74 |                         -0.12 |
| Feb 2026 |                0.42 |                -0.72 |                 -2.92 |               -2.38 |                  -4.97 |                      3.07 |            0.53 |            1.54 |               -1.50 |                           -0.24 |                        -4.66 |                   -0.74 |                                    0.45 |                                -9.96 |                                    0.85 |                         -0.03 |
| Mar 2026 |                0.22 |                -0.58 |                 -0.49 |               -1.89 |                  -5.55 |                      1.56 |            0.42 |            1.68 |               -1.47 |                            0.05 |                        -3.14 |                   -1.04 |                                    1.02 |                                -2.10 |                                    0.65 |                         -0.07 |
| Apr 2026 |                0.28 |                -1.62 |                  3.18 |                1.29 |                  -4.66 |                      1.35 |            0.97 |            2.31 |               -1.23 |                            0.17 |                        -0.16 |                   -0.82 |                                    0.13 |                                30.23 |                                    0.55 |                         -0.07 |
| May 2026 |                0.90 |                -3.13 |                  0.65 |                2.74 |                  -3.52 |                      0.79 |            0.88 |            2.63 |               -0.91 |                            0.23 |                        -0.39 |                   -1.17 |                                    0.33 |                                29.45 |                                    0.76 |                         -0.07 |
| Jun 2026 |                2.30 |                -3.04 |                  1.07 |                0.18 |                  -1.72 |                      0.92 |            1.09 |            3.04 |               -0.83 |                            0.31 |                        -0.93 |                   -1.11 |                                    0.42 |                                26.05 |                                    0.68 |                          0.04 |
| Jul 2026 |                2.82 |                -2.15 |                  0.59 |                3.28 |                  -0.15 |                      0.96 |            1.18 |            3.34 |               -0.54 |                            0.16 |                        -2.10 |                   -0.68 |                                    0.56 |                                23.23 |                                    0.76 |                          0.20 |
| Aug 2026 |                3.20 |                -1.36 |                  1.51 |                5.60 |                   0.78 |                      1.44 |            1.61 |            3.34 |               -0.53 |                            0.13 |                        -1.84 |                   -1.16 |                                    0.61 |                                20.80 |                                    0.75 |                          0.39 |
| Sep 2026 |                3.75 |                -0.21 |                  1.74 |                2.99 |                   0.84 |                      1.27 |            1.55 |            3.62 |               -0.29 |                            0.21 |                        -0.17 |                   -0.76 |                                    0.69 |                                18.61 |                                    0.81 |                          0.54 |
| Oct 2026 |                3.27 |                 1.33 |                  1.50 |                2.45 |                   0.53 |                      1.43 |            1.75 |            3.99 |               -0.31 |                            0.11 |                         0.87 |                   -1.15 |                                    0.89 |                                18.67 |                                    0.61 |                          0.70 |
| Nov 2026 |                4.41 |                 1.00 |                  3.26 |               -1.44 |                   1.28 |                      1.80 |            1.99 |            4.00 |               -0.19 |                            0.03 |                         0.67 |                   -1.38 |                                    0.64 |                                18.03 |                                    0.63 |                          0.84 |
| Dec 2026 |                4.41 |                 0.44 |                  2.21 |               -4.24 |                   2.61 |                      1.80 |            2.22 |            3.85 |               -0.14 |                            0.21 |                         1.02 |                   -1.18 |                                    0.86 |                                17.06 |                                    0.46 |                          1.00 |
| Jan 2027 |                3.59 |                 0.97 |                  1.97 |               -0.95 |                   2.09 |                      1.68 |            2.28 |            4.04 |               -0.22 |                            0.18 |                         0.74 |                   -0.99 |                                    0.70 |                                18.61 |                                    0.68 |                          1.14 |
| Feb 2027 |                3.45 |                 1.82 |                  3.81 |                2.09 |                   3.86 |                      1.05 |            2.46 |            4.23 |               -0.27 |                            0.20 |                         1.38 |                   -1.62 |                                    0.54 |                                18.68 |                                    0.61 |                          1.28 |
| Mar 2027 |                3.27 |                 0.78 |                  2.66 |                1.08 |                   3.23 |                      1.86 |            2.76 |            4.52 |               -0.33 |                            0.15 |                         2.12 |                   -0.90 |                                    0.13 |                                10.18 |                                    0.85 |                          1.43 |
| Apr 2027 |                3.52 |                 0.18 |                  0.37 |                0.77 |                   2.77 |                      1.30 |            2.29 |            3.86 |               -0.46 |                            0.17 |                         2.43 |                   -1.26 |                                    1.02 |                               -14.40 |                                    0.82 |                          1.57 |
| May 2027 |                2.77 |                 1.10 |                  1.35 |                1.87 |                   2.17 |                      1.65 |            2.40 |            2.98 |               -0.56 |                            0.00 |                         0.70 |                   -1.10 |                                    1.04 |                               -13.55 |                                    0.53 |                          1.72 |
| Jun 2027 |                2.17 |                 1.50 |                  1.61 |                1.98 |                   2.01 |                      1.66 |            2.43 |            2.72 |               -0.56 |                            0.00 |                         0.70 |                   -1.09 |                                    0.98 |                               -11.76 |                                    0.50 |                          1.75 |
| Jul 2027 |                1.99 |                 1.40 |                  1.63 |                1.39 |                   1.95 |                      1.63 |            2.44 |            2.55 |               -0.56 |                            0.00 |                         1.98 |                   -1.05 |                                    0.93 |                               -10.10 |                                    0.50 |                          1.75 |
| Aug 2027 |                1.84 |                 1.34 |                  1.54 |                0.97 |                   1.84 |                      1.60 |            2.44 |            2.42 |               -0.56 |                            0.00 |                         2.50 |                   -1.10 |                                    0.87 |                                -8.27 |                                    0.51 |                          1.75 |
| Sep 2027 |                1.80 |                 1.43 |                  1.51 |                1.09 |                   1.73 |                      1.59 |            2.43 |            2.32 |               -0.56 |                            0.00 |                         2.17 |                   -1.08 |                                    0.82 |                                -6.75 |                                    0.51 |                          1.74 |
| Oct 2027 |                1.76 |                 1.44 |                  1.55 |                0.98 |                   1.64 |                      1.59 |            2.43 |            2.26 |               -0.56 |                            0.00 |                         1.09 |                   -1.07 |                                    0.77 |                                -6.06 |                                    0.51 |                          1.74 |
| Nov 2027 |                1.75 |                 1.42 |                  1.44 |                1.37 |                   1.64 |                      1.60 |            2.43 |            2.20 |               -0.56 |                            0.00 |                         0.79 |                   -1.10 |                                    0.73 |                                -4.83 |                                    0.51 |                          1.74 |
| Dec 2027 |                1.74 |                 1.43 |                  1.53 |                1.71 |                   1.70 |                      1.62 |            2.42 |            2.15 |               -0.56 |                            0.00 |                         1.34 |                   -1.10 |                                    0.68 |                                -3.73 |                                    0.50 |                          1.74 |

**Table 7: Quarterly Component YoY Growth (%) — 2026 to 2027**

| date     |   Rice Flour Cereal |   Meats Poultry Fish |   Eggs Dairy Products |   Vegetables Fruits |   Seasoning Condiments |   Non Alcoholic Beverages |   Sugar Product |   Prepared Food |   Apparel Footwears |   Housing Furnishing ex Utility |   Housing Furnishing Utility |   Medical Personal Care |   Transport Communication ex Motor Fuel |   Transport Communication Motor Fuel |   Recreation Reading Education Religion |   Tobacco Alcoholic Beverages |
|:---------|--------------------:|---------------------:|----------------------:|--------------------:|-----------------------:|--------------------------:|----------------:|----------------:|--------------------:|--------------------------------:|-----------------------------:|------------------------:|----------------------------------------:|-------------------------------------:|----------------------------------------:|------------------------------:|
| Mar 2026 |                0.08 |                -0.20 |                 -1.72 |               -1.45 |                  -4.11 |                      2.37 |            0.60 |            1.65 |               -1.55 |                           -0.11 |                        -4.16 |                   -1.03 |                                    0.67 |                                -7.43 |                                    0.75 |                         -0.07 |
| Jun 2026 |                1.16 |                -2.60 |                  1.62 |                1.40 |                  -3.31 |                      1.02 |            0.98 |            2.66 |               -0.99 |                            0.23 |                        -0.49 |                   -1.03 |                                    0.29 |                                28.58 |                                    0.66 |                         -0.03 |
| Sep 2026 |                3.26 |                -1.25 |                  1.28 |                3.95 |                   0.49 |                      1.22 |            1.44 |            3.43 |               -0.45 |                            0.17 |                        -1.37 |                   -0.86 |                                    0.62 |                                20.88 |                                    0.77 |                          0.38 |
| Dec 2026 |                4.03 |                 0.92 |                  2.32 |               -1.12 |                   1.47 |                      1.68 |            1.99 |            3.95 |               -0.21 |                            0.11 |                         0.85 |                   -1.24 |                                    0.79 |                                17.92 |                                    0.57 |                          0.85 |
| Mar 2027 |                3.44 |                 1.19 |                  2.81 |                0.72 |                   3.05 |                      1.53 |            2.50 |            4.26 |               -0.27 |                            0.18 |                         1.41 |                   -1.17 |                                    0.45 |                                15.69 |                                    0.71 |                          1.28 |
| Jun 2027 |                2.82 |                 0.93 |                  1.11 |                1.54 |                   2.31 |                      1.54 |            2.38 |            3.18 |               -0.53 |                            0.06 |                         1.27 |                   -1.15 |                                    1.01 |                               -13.26 |                                    0.62 |                          1.68 |
| Sep 2027 |                1.88 |                 1.39 |                  1.56 |                1.15 |                   1.84 |                      1.61 |            2.44 |            2.43 |               -0.56 |                            0.00 |                         2.22 |                   -1.08 |                                    0.87 |                                -8.39 |                                    0.51 |                          1.75 |
| Dec 2027 |                1.75 |                 1.43 |                  1.51 |                1.35 |                   1.66 |                      1.60 |            2.43 |            2.20 |               -0.56 |                            0.00 |                         1.07 |                   -1.09 |                                    0.73 |                                -4.88 |                                    0.51 |                          1.74 |

**Table 8: Annual Component YoY Growth (%) — 2021 to 2027**

|      |   Rice Flour Cereal |   Meats Poultry Fish |   Eggs Dairy Products |   Vegetables Fruits |   Seasoning Condiments |   Non Alcoholic Beverages |   Sugar Product |   Prepared Food |   Apparel Footwears |   Housing Furnishing ex Utility |   Housing Furnishing Utility |   Medical Personal Care |   Transport Communication ex Motor Fuel |   Transport Communication Motor Fuel |   Recreation Reading Education Religion |   Tobacco Alcoholic Beverages |
|-----:|--------------------:|---------------------:|----------------------:|--------------------:|-----------------------:|--------------------------:|----------------:|----------------:|--------------------:|--------------------------------:|-----------------------------:|------------------------:|----------------------------------------:|-------------------------------------:|----------------------------------------:|------------------------------:|
| 2021 |               -6.71 |                 0.80 |                  0.68 |               -0.42 |                   4.30 |                     -0.24 |            0.98 |            0.44 |               -0.26 |                           -0.55 |                        -7.33 |                    0.23 |                                    1.29 |                                24.59 |                                   -0.44 |                          0.28 |
| 2022 |               -0.91 |                11.64 |                  6.91 |                4.21 |                   8.64 |                      2.81 |            7.53 |            7.31 |                0.04 |                            1.62 |                        20.79 |                    1.12 |                                    2.05 |                                23.93 |                                    0.23 |                          2.01 |
| 2023 |                4.06 |                -2.41 |                  7.49 |                7.84 |                  -2.16 |                      3.72 |            2.51 |            3.11 |                0.24 |                            0.58 |                         3.89 |                    1.58 |                                    0.14 |                                -2.94 |                                    0.96 |                          0.80 |
| 2024 |                2.73 |                -2.82 |                  2.27 |                2.28 |                  -0.56 |                      2.28 |            2.81 |            1.42 |               -0.40 |                           -0.03 |                        -0.85 |                    0.11 |                                    0.20 |                                 0.67 |                                    0.55 |                          1.23 |
| 2025 |                0.47 |                 2.53 |                 -2.41 |               -5.25 |                   3.54 |                      3.57 |            1.74 |            2.45 |               -0.94 |                            0.02 |                        -1.24 |                   -0.83 |                                    0.03 |                                -5.87 |                                    0.55 |                          0.07 |
| 2026 |                2.12 |                -0.80 |                  0.87 |                0.66 |                  -1.40 |                      1.57 |            1.25 |            2.93 |               -0.80 |                            0.10 |                        -1.32 |                   -1.04 |                                    0.59 |                                14.67 |                                    0.69 |                          0.28 |
| 2027 |                2.46 |                 1.23 |                  1.74 |                1.19 |                   2.21 |                      1.57 |            2.44 |            3.01 |               -0.48 |                            0.06 |                         1.49 |                   -1.12 |                                    0.77 |                                -3.79 |                                    0.59 |                          1.61 |

---

### Appendix C: Model Summary by Component

#### Rice Flour Cereal

```
                               SARIMAX Results                                
==============================================================================
Dep. Variable:                      y   No. Observations:                  605
Model:               SARIMAX(2, 1, 1)   Log Likelihood                -584.033
Date:                Thu, 11 Jun 2026   AIC                           1178.066
Time:                        15:29:32   BIC                           1200.084
Sample:                    01-01-1976   HQIC                          1186.634
                         - 05-01-2026                                         
Covariance Type:                  opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
intercept      0.1161      0.060      1.933      0.053      -0.002       0.234
ar.L1          0.0147      0.069      0.213      0.831      -0.121       0.150
ar.L2          0.2334      0.050      4.699      0.000       0.136       0.331
ma.L1          0.6864      0.069      9.904      0.000       0.551       0.822
sigma2         0.4046      0.006     69.683      0.000       0.393       0.416
===================================================================================
Ljung-Box (L1) (Q):                   0.04   Jarque-Bera (JB):             73376.09
Prob(Q):                              0.84   Prob(JB):                         0.00
Heteroskedasticity (H):               3.68   Skew:                             4.47
Prob(H) (two-sided):                  0.00   Kurtosis:                        56.25
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).
```

#### Meats Poultry Fish

```
                                      SARIMAX Results                                       
============================================================================================
Dep. Variable:                                    y   No. Observations:                  605
Model:             SARIMAX(2, 1, 2)x(1, 0, [1], 12)   Log Likelihood                -556.782
Date:                              Thu, 11 Jun 2026   AIC                           1129.563
Time:                                      15:29:50   BIC                           1164.792
Sample:                                  01-01-1976   HQIC                          1143.273
                                       - 05-01-2026                                         
Covariance Type:                                opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
intercept      0.0143      0.018      0.774      0.439      -0.022       0.050
ar.L1         -0.6293      0.212     -2.973      0.003      -1.044      -0.214
ar.L2         -0.3261      0.078     -4.202      0.000      -0.478      -0.174
ma.L1          0.9480      0.213      4.459      0.000       0.531       1.365
ma.L2          0.4874      0.059      8.250      0.000       0.372       0.603
ar.S.L12       0.9445      0.044     21.345      0.000       0.858       1.031
ma.S.L12      -0.8484      0.059    -14.290      0.000      -0.965      -0.732
sigma2         0.3679      0.007     55.470      0.000       0.355       0.381
===================================================================================
Ljung-Box (L1) (Q):                   0.01   Jarque-Bera (JB):             87450.05
Prob(Q):                              0.93   Prob(JB):                         0.00
Heteroskedasticity (H):              16.94   Skew:                             3.80
Prob(H) (two-sided):                  0.00   Kurtosis:                        61.46
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).
```

#### Eggs Dairy Products

```
                                     SARIMAX Results                                      
==========================================================================================
Dep. Variable:                                  y   No. Observations:                  605
Model:             SARIMAX(0, 1, 1)x(2, 0, 1, 12)   Log Likelihood                -695.464
Date:                            Thu, 11 Jun 2026   AIC                           1402.928
Time:                                    15:30:02   BIC                           1429.350
Sample:                                01-01-1976   HQIC                          1413.211
                                     - 05-01-2026                                         
Covariance Type:                              opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
intercept      0.0039      0.005      0.821      0.412      -0.005       0.013
ma.L1          0.2479      0.029      8.439      0.000       0.190       0.306
ar.S.L12       0.8975      0.043     20.823      0.000       0.813       0.982
ar.S.L24       0.0713      0.033      2.186      0.029       0.007       0.135
ma.S.L12      -0.8845      0.045    -19.487      0.000      -0.974      -0.796
sigma2         0.5802      0.017     33.221      0.000       0.546       0.614
===================================================================================
Ljung-Box (L1) (Q):                   1.53   Jarque-Bera (JB):              2208.78
Prob(Q):                              0.22   Prob(JB):                         0.00
Heteroskedasticity (H):               1.72   Skew:                             0.50
Prob(H) (two-sided):                  0.00   Kurtosis:                        12.32
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).
```

#### Vegetables Fruits

```
                                     SARIMAX Results                                      
==========================================================================================
Dep. Variable:                                  y   No. Observations:                  605
Model:             SARIMAX(1, 1, 2)x(1, 0, 2, 12)   Log Likelihood               -1131.594
Date:                            Thu, 11 Jun 2026   AIC                           2277.189
Time:                                    15:30:43   BIC                           2308.014
Sample:                                01-01-1976   HQIC                          2289.185
                                     - 05-01-2026                                         
Covariance Type:                              opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
ar.L1          0.5457      0.089      6.134      0.000       0.371       0.720
ma.L1         -0.5334      0.093     -5.728      0.000      -0.716      -0.351
ma.L2         -0.1920      0.031     -6.178      0.000      -0.253      -0.131
ar.S.L12       0.9695      0.018     54.409      0.000       0.935       1.004
ma.S.L12      -0.9434      0.037    -25.295      0.000      -1.017      -0.870
ma.S.L24       0.1020      0.030      3.420      0.001       0.044       0.160
sigma2         2.4454      0.087     28.094      0.000       2.275       2.616
===================================================================================
Ljung-Box (L1) (Q):                   0.01   Jarque-Bera (JB):               451.11
Prob(Q):                              0.94   Prob(JB):                         0.00
Heteroskedasticity (H):              23.80   Skew:                             0.33
Prob(H) (two-sided):                  0.00   Kurtosis:                         7.18
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).
```

#### Seasoning Condiments

```
                                     SARIMAX Results                                      
==========================================================================================
Dep. Variable:                                  y   No. Observations:                  605
Model:             SARIMAX(3, 1, 0)x(1, 0, 0, 12)   Log Likelihood                -433.325
Date:                            Thu, 11 Jun 2026   AIC                            878.651
Time:                                    15:30:57   BIC                            905.072
Sample:                                01-01-1976   HQIC                           888.933
                                     - 05-01-2026                                         
Covariance Type:                              opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
intercept      0.0640      0.028      2.295      0.022       0.009       0.119
ar.L1          0.3038      0.023     13.150      0.000       0.259       0.349
ar.L2         -0.0278      0.018     -1.562      0.118      -0.063       0.007
ar.L3          0.2022      0.026      7.820      0.000       0.152       0.253
ar.S.L12       0.0755      0.034      2.205      0.027       0.008       0.143
sigma2         0.2457      0.005     49.253      0.000       0.236       0.255
===================================================================================
Ljung-Box (L1) (Q):                   0.07   Jarque-Bera (JB):             53897.01
Prob(Q):                              0.79   Prob(JB):                         0.00
Heteroskedasticity (H):               0.91   Skew:                            -2.85
Prob(H) (two-sided):                  0.49   Kurtosis:                        48.93
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).
```

#### Non Alcoholic Beverages

```
                               SARIMAX Results                                
==============================================================================
Dep. Variable:                      y   No. Observations:                  605
Model:               SARIMAX(3, 1, 2)   Log Likelihood                -320.841
Date:                Thu, 11 Jun 2026   AIC                            655.681
Time:                        15:31:08   BIC                            686.506
Sample:                    01-01-1976   HQIC                           667.677
                         - 05-01-2026                                         
Covariance Type:                  opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
intercept      0.0371      0.009      4.232      0.000       0.020       0.054
ar.L1          1.7515      0.040     43.936      0.000       1.673       1.830
ar.L2         -1.0829      0.065    -16.718      0.000      -1.210      -0.956
ar.L3          0.0787      0.037      2.112      0.035       0.006       0.152
ma.L1         -1.6545      0.033    -50.591      0.000      -1.719      -1.590
ma.L2          0.9615      0.032     30.287      0.000       0.899       1.024
sigma2         0.1695      0.004     38.215      0.000       0.161       0.178
===================================================================================
Ljung-Box (L1) (Q):                   0.00   Jarque-Bera (JB):             22249.48
Prob(Q):                              0.95   Prob(JB):                         0.00
Heteroskedasticity (H):               0.20   Skew:                             4.20
Prob(H) (two-sided):                  0.00   Kurtosis:                        31.52
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).
```

#### Sugar Product

```
                               SARIMAX Results                                
==============================================================================
Dep. Variable:                      y   No. Observations:                  294
Model:               SARIMAX(1, 1, 0)   Log Likelihood                -207.263
Date:                Thu, 11 Jun 2026   AIC                            420.526
Time:                        15:31:09   BIC                            431.567
Sample:                    12-01-2001   HQIC                           424.948
                         - 05-01-2026                                         
Covariance Type:                  opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
intercept      0.1468      0.062      2.381      0.017       0.026       0.268
ar.L1          0.3203      0.033      9.762      0.000       0.256       0.385
sigma2         0.2409      0.010     24.679      0.000       0.222       0.260
===================================================================================
Ljung-Box (L1) (Q):                   0.01   Jarque-Bera (JB):             10323.91
Prob(Q):                              0.93   Prob(JB):                         0.00
Heteroskedasticity (H):               2.76   Skew:                             4.41
Prob(H) (two-sided):                  0.00   Kurtosis:                        30.71
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).
```

#### Prepared Food

```
                                      SARIMAX Results                                       
============================================================================================
Dep. Variable:                                    y   No. Observations:                  605
Model:             SARIMAX(1, 1, 2)x(1, 0, [1], 12)   Log Likelihood                 -95.507
Date:                              Thu, 11 Jun 2026   AIC                            205.013
Time:                                      15:31:36   BIC                            235.838
Sample:                                  01-01-1976   HQIC                           217.009
                                       - 05-01-2026                                         
Covariance Type:                                opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
intercept      0.0140      0.011      1.249      0.212      -0.008       0.036
ar.L1          0.7863      0.083      9.494      0.000       0.624       0.949
ma.L1         -0.4830      0.084     -5.759      0.000      -0.647      -0.319
ma.L2         -0.0859      0.050     -1.726      0.084      -0.183       0.012
ar.S.L12       0.5862      0.252      2.325      0.020       0.092       1.080
ma.S.L12      -0.4899      0.270     -1.816      0.069      -1.019       0.039
sigma2         0.0803      0.002     53.089      0.000       0.077       0.083
===================================================================================
Ljung-Box (L1) (Q):                   0.00   Jarque-Bera (JB):             57048.88
Prob(Q):                              0.99   Prob(JB):                         0.00
Heteroskedasticity (H):               3.71   Skew:                             4.78
Prob(H) (two-sided):                  0.00   Kurtosis:                        49.64
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).
```

#### Apparel Footwears

```
                               SARIMAX Results                                
==============================================================================
Dep. Variable:                      y   No. Observations:                  605
Model:               SARIMAX(1, 2, 2)   Log Likelihood                 -46.176
Date:                Thu, 11 Jun 2026   AIC                            100.352
Time:                        15:31:40   BIC                            117.959
Sample:                    01-01-1976   HQIC                           107.205
                         - 05-01-2026                                         
Covariance Type:                  opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
ar.L1         -0.9742      0.046    -21.212      0.000      -1.064      -0.884
ma.L1          0.0633      0.058      1.100      0.271      -0.049       0.176
ma.L2         -0.8511      0.059    -14.346      0.000      -0.967      -0.735
sigma2         0.0680      0.001     98.386      0.000       0.067       0.069
===================================================================================
Ljung-Box (L1) (Q):                   0.80   Jarque-Bera (JB):            112574.87
Prob(Q):                              0.37   Prob(JB):                         0.00
Heteroskedasticity (H):               0.21   Skew:                            -3.23
Prob(H) (two-sided):                  0.00   Kurtosis:                        69.63
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).
```

#### Housing Furnishing ex Utility

```
                               SARIMAX Results                                
==============================================================================
Dep. Variable:                      y   No. Observations:                  233
Model:               SARIMAX(0, 1, 0)   Log Likelihood                -301.473
Date:                Thu, 11 Jun 2026   AIC                            604.946
Time:                        15:31:41   BIC                            608.393
Sample:                    01-01-2007   HQIC                           606.336
                         - 05-01-2026                                         
Covariance Type:                  opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
sigma2         0.7874      0.009     87.378      0.000       0.770       0.805
===================================================================================
Ljung-Box (L1) (Q):                   0.00   Jarque-Bera (JB):            171274.48
Prob(Q):                              0.98   Prob(JB):                         0.00
Heteroskedasticity (H):               0.08   Skew:                            -9.72
Prob(H) (two-sided):                  0.00   Kurtosis:                       134.68
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).
```

#### Housing Furnishing Utility

```
                               SARIMAX Results                                
==============================================================================
Dep. Variable:                      y   No. Observations:                  605
Model:               SARIMAX(3, 1, 4)   Log Likelihood               -1406.414
Date:                Thu, 11 Jun 2026   AIC                           2830.827
Time:                        15:32:01   BIC                           2870.459
Sample:                    01-01-1976   HQIC                          2846.251
                         - 05-01-2026                                         
Covariance Type:                  opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
intercept      0.2621      0.286      0.918      0.359      -0.298       0.822
ar.L1          0.0158      0.081      0.195      0.846      -0.143       0.175
ar.L2         -0.3086      0.058     -5.365      0.000      -0.421      -0.196
ar.L3         -0.7263      0.070    -10.341      0.000      -0.864      -0.589
ma.L1         -0.1045      0.086     -1.219      0.223      -0.273       0.064
ma.L2          0.1702      0.060      2.818      0.005       0.052       0.289
ma.L3          0.8491      0.062     13.665      0.000       0.727       0.971
ma.L4         -0.1066      0.030     -3.513      0.000      -0.166      -0.047
sigma2         6.1419      0.112     54.868      0.000       5.923       6.361
===================================================================================
Ljung-Box (L1) (Q):                   0.00   Jarque-Bera (JB):            138270.82
Prob(Q):                              0.96   Prob(JB):                         0.00
Heteroskedasticity (H):              19.86   Skew:                            -4.59
Prob(H) (two-sided):                  0.00   Kurtosis:                        76.55
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).
```

#### Medical Personal Care

```
                                     SARIMAX Results                                      
==========================================================================================
Dep. Variable:                                  y   No. Observations:                  605
Model:             SARIMAX(0, 2, 2)x(0, 0, 2, 12)   Log Likelihood                 -11.284
Date:                            Thu, 11 Jun 2026   AIC                             32.568
Time:                                    15:32:13   BIC                             54.578
Sample:                                01-01-1976   HQIC                            41.134
                                     - 05-01-2026                                         
Covariance Type:                              opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
ma.L1         -1.0062      0.043    -23.603      0.000      -1.090      -0.923
ma.L2          0.0875      0.042      2.088      0.037       0.005       0.170
ma.S.L12       0.1207      0.039      3.070      0.002       0.044       0.198
ma.S.L24       0.0940      0.051      1.846      0.065      -0.006       0.194
sigma2         0.0606      0.001     81.245      0.000       0.059       0.062
===================================================================================
Ljung-Box (L1) (Q):                   0.00   Jarque-Bera (JB):             96084.27
Prob(Q):                              0.97   Prob(JB):                         0.00
Heteroskedasticity (H):               0.41   Skew:                             4.78
Prob(H) (two-sided):                  0.00   Kurtosis:                        64.10
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).
```

#### Transport Communication ex Motor Fuel

```
                               SARIMAX Results                                
==============================================================================
Dep. Variable:                      y   No. Observations:                  233
Model:               SARIMAX(2, 0, 0)   Log Likelihood                -566.719
Date:                Thu, 11 Jun 2026   AIC                           1141.437
Time:                        15:32:16   BIC                           1155.241
Sample:                    01-01-2007   HQIC                          1147.004
                         - 05-01-2026                                         
Covariance Type:                  opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
intercept      5.3349      2.367      2.254      0.024       0.696       9.974
ar.L1          1.0468      0.031     33.542      0.000       0.986       1.108
ar.L2         -0.0989      0.038     -2.618      0.009      -0.173      -0.025
sigma2         7.5120      0.170     44.181      0.000       7.179       7.845
===================================================================================
Ljung-Box (L1) (Q):                   0.01   Jarque-Bera (JB):             16829.73
Prob(Q):                              0.94   Prob(JB):                         0.00
Heteroskedasticity (H):               0.01   Skew:                             3.17
Prob(H) (two-sided):                  0.00   Kurtosis:                        44.15
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).
```

#### Transport Communication Motor Fuel

```
                               SARIMAX Results                                
==============================================================================
Dep. Variable:                      y   No. Observations:                  221
Model:               SARIMAX(1, 1, 1)   Log Likelihood                -559.240
Date:                Thu, 11 Jun 2026   AIC                           1126.479
Time:                        15:32:19   BIC                           1140.054
Sample:                    01-01-2008   HQIC                          1131.961
                         - 05-01-2026                                         
Covariance Type:                  opg                                         
====================================================================================
                       coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------------
exog_dubai_crude     0.3252      0.012     26.957      0.000       0.302       0.349
ar.L1                0.6831      0.160      4.282      0.000       0.370       0.996
ma.L1               -0.8552      0.133     -6.442      0.000      -1.115      -0.595
sigma2               9.4429      0.464     20.354      0.000       8.534      10.352
===================================================================================
Ljung-Box (L1) (Q):                   0.00   Jarque-Bera (JB):             23606.76
Prob(Q):                              0.99   Prob(JB):                         0.00
Heteroskedasticity (H):               2.97   Skew:                             4.16
Prob(H) (two-sided):                  0.00   Kurtosis:                        53.06
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).
```

#### Recreation Reading Education Religion

```
                                     SARIMAX Results                                      
==========================================================================================
Dep. Variable:                                  y   No. Observations:                  605
Model:             SARIMAX(1, 2, 1)x(1, 0, 1, 12)   Log Likelihood                -541.526
Date:                            Thu, 11 Jun 2026   AIC                           1093.053
Time:                                    15:32:47   BIC                           1115.062
Sample:                                01-01-1976   HQIC                          1101.619
                                     - 05-01-2026                                         
Covariance Type:                              opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
ar.L1          0.0792      0.036      2.206      0.027       0.009       0.150
ma.L1         -0.9848      0.016    -60.671      0.000      -1.017      -0.953
ar.S.L12       0.7496      0.161      4.662      0.000       0.434       1.065
ma.S.L12      -0.6759      0.190     -3.560      0.000      -1.048      -0.304
sigma2         0.3509      0.004     93.354      0.000       0.344       0.358
===================================================================================
Ljung-Box (L1) (Q):                   0.00   Jarque-Bera (JB):            874047.04
Prob(Q):                              0.97   Prob(JB):                         0.00
Heteroskedasticity (H):               0.08   Skew:                            -8.64
Prob(H) (two-sided):                  0.00   Kurtosis:                       188.71
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).
```

#### Tobacco Alcoholic Beverages

```
                               SARIMAX Results                                
==============================================================================
Dep. Variable:                      y   No. Observations:                  605
Model:               SARIMAX(0, 1, 1)   Log Likelihood                -489.607
Date:                Thu, 11 Jun 2026   AIC                            985.214
Time:                        15:32:49   BIC                            998.425
Sample:                    01-01-1976   HQIC                           990.355
                         - 05-01-2026                                         
Covariance Type:                  opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
intercept      0.1479      0.055      2.689      0.007       0.040       0.256
ma.L1          0.2997      0.021     14.424      0.000       0.259       0.340
sigma2         0.2962      0.006     53.516      0.000       0.285       0.307
===================================================================================
Ljung-Box (L1) (Q):                   0.07   Jarque-Bera (JB):             94553.84
Prob(Q):                              0.80   Prob(JB):                         0.00
Heteroskedasticity (H):               4.99   Skew:                             6.47
Prob(H) (two-sided):                  0.00   Kurtosis:                        62.91
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).
```


---
*Report generated by NESDC CPI Forecasting Pipeline (`src/pipeline/cpi_forecast/`)*

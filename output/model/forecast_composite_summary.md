# Export & Import Composite Price Indices Aggregation

This document details the aggregation of forecasted price component indices into their respective composite Export and Import Price Indices, projected on the official BOT series.

## ⚖️ Weighting Scheme (Naive Method)
The future weights are assumed to remain constant at the latest known historical data point (**2026-04-01**):

### 🚢 Export Weights
- **Agro Industrial**: 7.0300%
- **Agricultural**: 8.1900%
- **Mineral Fuel**: 3.9400%
- **Principal Manuf**: 80.8400%

### 📥 Import Weights
- **Capital Goods**: 25.7000%
- **Consumer Goods**: 10.9100%
- **Fuel**: 17.6900%
- **Raw Materials**: 42.1900%
- **Vehicle Equip**: 3.5100%

## 🔗 Aggregation & Splicing Methodology
Direct raw weighted average aggregation creates level shifts due to chain-weighting discrepancy in historical index series published by the Ministry of Commerce. To preserve level continuity, we apply a splicing ratio factor defined as:

$$\text{Ratio} = \frac{\text{Actual Composite Index at Overlap}}{\text{Raw Weighted Average Index at Overlap}}$$

- **Export Splicing Ratio**: `0.989805` (Actual 114.80 vs. Weighted 115.98)
- **Import Splicing Ratio**: `0.973504` (Actual 128.10 vs. Weighted 131.59)

## 🏦 BOT Official Price Indices Forecast (Growth Spliced)
Projected by applying the growth rate of the spliced CEIC composite index to the latest actual BOT value on April 2026:

| Month | BOT Export Price Index Forecast | BOT Import Price Index Forecast |
|---|---|---|
| 2026-05-01 | 114.6748 | 127.6770 |
| 2026-06-01 | 114.7485 | 128.4800 |
| 2026-07-01 | 114.6862 | 128.7499 |
| 2026-08-01 | 114.8372 | 128.8664 |
| 2026-09-01 | 114.9288 | 129.0029 |
| 2026-10-01 | 114.8786 | 129.2456 |
| 2026-11-01 | 114.9441 | 129.5549 |
| 2026-12-01 | 115.1079 | 129.6422 |
| 2027-01-01 | 115.2077 | 130.0514 |
| 2027-02-01 | 115.2409 | 130.2943 |
| 2027-03-01 | 115.3120 | 130.4925 |
| 2027-04-01 | 115.3897 | 130.8472 |
| 2027-05-01 | 115.5498 | 131.1321 |
| 2027-06-01 | 115.6128 | 131.4401 |
| 2027-07-01 | 115.5496 | 131.6314 |
| 2027-08-01 | 115.6473 | 132.0100 |
| 2027-09-01 | 115.7929 | 132.4587 |
| 2027-10-01 | 115.7446 | 132.5596 |
| 2027-11-01 | 115.7851 | 132.9082 |
| 2027-12-01 | 115.9985 | 133.3802 |

# Data Transformation Troubleshooting

This document records known errors, pitfalls, and solutions for data transformation processes in this workspace.

## Seasonal Adjustment (X13-ARIMA-SEATS)
- **Minimum Data Requirement**: X13 typically requires at least 3 years (36 months or 12 quarters) of data to produce reliable results.
- **Frequency Integrity**: Ensure the DataFrame has a regular frequency (no missing periods) before calling X13. Use `.asfreq()` or resampling.
- **Binary Path**: Always use the absolute path to `bin/x13as.exe`.

## Frequency Conversion
- **Aggregation Choice**: 
    - Use `mean()` for indices/prices (CPI, Exchange Rates).
    - Use `sum()` for flow variables (GDP, Exports, Revenue).
    - Use `last()` for end-of-period stocks.

## Merging & Joining
- **Date Alignment**: When merging multiple series (e.g., for currency conversion), ensure dates are aligned. Use `outer` joins to preserve data, then handle NAs.
- **Deduplication**: Always `.drop_duplicates(subset=['date'])` before pivoting or joining to avoid `ValueError`.

## Currency Conversion
- **Base/Quote Direction**: Always verify if the exchange rate is `Local/USD` (e.g., THB/USD) or `USD/Local`. Multiplication vs. Division depends on this direction.
- **Frequency Mismatch**: Exchange rates are often daily, while economic data is monthly/quarterly. Use `.ffill()` or `.reindex(method='ffill')` after merging to ensure every data point has a corresponding rate.
- **Base Currency Consistency**: Ensure all series being compared are converted to the same base currency using the same source of exchange rates to maintain internal consistency.

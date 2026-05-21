# Trade Analysis Reference: GTA Database Schema & Metrics

## 1. GTA Database Schema (`database/GTA.db`)

### Table: `GTA` (Main Trade Data)
- `Reporter`: ISO3 code of the reporting country.
- `Partner`: ISO3 code of the partner country.
- `HS_Code`: Harmonized System code (usually HS6 or HS2).
- `Flow`: Trade direction ('Export' or 'Import').
- `Year`: Calendar year.
- `Month`: Month (1-12).
- `Value`: Trade value (usually in USD).
- `Quantity`: Trade volume (if available).

### Table: `meta_hs2` (HS2 Classifications)
- `HS2_Code`: 2-digit HS code (Integer).
- `HS2_Desc_EN`: English description.
- `HS2_Desc_TH`: Thai description.

### Table: `meta_iso` (Country Codes)
- `ISO3`: 3-letter country code.
- `Country_Name_EN`: English name.
- `Region`: Geographic region.

## 2. Common Trade Metrics & Formulas

### Revealed Comparative Advantage (RCA)
Measures a country's relative export performance in a specific product.
`RCA = (X_ij / X_it) / (X_wj / X_wt)`
- `X_ij`: Country i's exports of product j.
- `X_it`: Country i's total exports.
- `X_wj`: World exports of product j.
- `X_wt`: Total world exports.
*Interpretation: RCA > 1 indicates comparative advantage.*

### Trade Balance
`Trade Balance = Exports - Imports`

### Market Share
`Market Share = (Country i's Exports to Partner p / World Exports to Partner p) * 100`

## 3. SQL Query Patterns

### Joining HS Descriptions
```sql
SELECT t.*, h.HS2_Desc_EN
FROM GTA t
JOIN meta_hs2 h ON CAST(SUBSTR(printf('%02d', t.HS_Code), 1, 2) AS INTEGER) = h.HS2_Code
WHERE t.Year = 2023;
```

### Joining Country Names
```sql
SELECT t.*, m.Country_Name_EN as Reporter_Name
FROM GTA t
JOIN meta_iso m ON t.Reporter = m.ISO3;
```

# Country Specific Economic Report Structure

This .md contains structure template of country economic report. If user wants to create an economic report for a specific country, use this template as an outline. However, since each country may not have all the data listed in this template, if you cannot find a requested series after few attemps, you should skip it rather than keep finding it and waste tokens.

## Executive Summary

- Overall economic outlook [AI summary from different sections of the report]

## GDP

### Overall growth

- Latest quarterly real GDP growth (%YoY) [Vertical Bar Chart with data lable - get data from CEIC]
- Overall summary [analytical report from https://tradingeconomics.com/[country name]/gdp-growth-annual]
  
### Expenditure Side

- YoY Growth by expenditure component [Table - get data from CEIC]
- Share by expenditure component [Table - get data from CEIC]
- Contribution to growth by expenditure component [Stacked bar chart - get data from CEIC]

### Production Side

- YoY Growth by production component [Table - get data from CEIC]
- Share by production component [Table - get data from CEIC]
- Contribution to growth by production component [Stacked bar chart - get data from CEIC]

### Annual Growth

- Annual real GDP growth [Verical bar chart with data lable - get data from CEIC]

## Foreign Trade

### Exports

- Monthly Total Export: BOP basis (%YoY) [Verical bar chart with data lable - get data from CEIC]
- Top 10 Exports of the last year by HS2 [Table - get data from GTA.db]
- Contribution to growth of Exports by HS2 (only top 5 and group others to others + add footnote to Appendix: Contribution to growth of Exports and Imports by HS2) [Stacked bar chart - get data from GTA.db]
- Top 10 Exports of the last year by country [Table - get data from GTA.db]
- Contribution to growth of Exports by country (only top 5 and group others to others + add footnote to Appendix: Contribution to growth of Exports and Imports by country) [Stacked bar chart - get data from GTA.db]

### Imports

- Monthly Total Import: BOP basis (%YoY) [Verical bar chart with data lable - get data from CEIC]
- Top 10 Imports of the last year by HS2 [Table - get data from GTA.db]
- Contribution to growth of Imports by HS2 (only top 5 and group others to others + add footnote to Appendix: Contribution to growth of Exports and Imports by HS2) [Stacked bar chart - get data from GTA.db]
- Top 10 Imports of the last year by country [Table - get data from GTA.db]
- Contribution to growth of Imports by country (only top 5 and group others to others + add footnote to Appendix: Contribution to growth of Exports and Imports by country) [Stacked bar chart - get data from GTA.db]

### Trade Balance

- Monthly Total Exports, Total Imports, and Trade Balance in USD [2 vertical sub plot: Above chart -> line chart of total exports and imports values/ Below chart -> vertical bar chart of trade balance]

## Fiscal Policy

- fiscal policies implimenting or planned to be implemeting. (give information on implimenting date too) [general web search]

## Inflation, Exchange rate, and Monetary Policy

### Consumer Price Index (CPI)

- Monthly CPI growth YoY with long-run average line and Central bank target line [Vertical bar chart - get data from CEIC]
- Monthly Contribution to growth of CPI by main group of component [Stacked bar chart - get data from CEIC]
- Monthly policy rate [Line chart]
- Monetary stance and decision [summarize from: https://tradingeconomics.com/[country name]/interest-rate]

### Producer Price Index (PPI)

- Monthly Producer price index and CPI growth YoY in the same chart [line chart]

### Exchange rate

- Monthly average Local Exchange rate against USD with horizontal long run mean [line chart]

## Labor Market

Data Table of ...

- Unemployment rate
- Labor force participation rate
- Real Wage

## Leading Indicators

Data Table of ...

- Yield curve (10-year minus 2-year or 3-month Treasury spread)
- Consumer Confidence Index
- Stock market performance (Monthly average)

## Purchasing Manager Indices

In this part I want heatmap of monthly different indicators (seasonal adjusted series only). User should be the one providing S&P API endpoint. If user doesn't provide the endpoint (or forget to), ask user for it.

---

## Appendix

### Contribution to growth of Exports and Imports by HS2

- Contribution to growth of Exports by HS2 (sorted by largest to smallest contribution)
- Contribution to growth of Imports by HS2 (sorted by largest to smallest contribution)

### Contribution to growth of Exports and Imports by country

- Contribution to growth of Exports by country (sorted by largest to smallest contribution)
- Contribution to growth of Imports by country (sorted by largest to smallest contribution)

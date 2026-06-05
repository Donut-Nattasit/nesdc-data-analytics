# CEIC Search Heuristics

Use these patterns to filter results efficiently and avoid "Trade Partner" noise.

## 1. Eliminating Trade Partner Noise
When searching for "Exports: China", the API often returns "Exports: to China" from other countries.
- **Auto-Refinement**: If noise is detected, append `fob`, `Customs Basis`, or `Total` to the keyword.
- **Keyword Patterns**: Use `Exports: fob: [Country]` or `Trade Balance: Export: [Country]`.
- **Exclusionary Logic**: Be wary of names containing `to`, `from`, `partner`, or `destination` unless bilateral trade is specifically requested.

## 2. Targeting Frequency
- **GDP**: Always include `Quarterly` or `Annual` in the keyword (e.g., `Real GDP Quarterly Thailand`).
- **Inflation/Trade**: Include `Monthly` (e.g., `CPI Monthly YoY Vietnam`).

## 3. Disambiguating Metrics
- **Real vs Nominal**: Prioritize `Real` (or `Constant Prices`) for growth analysis. Use `Nominal` (or `Current Prices`) for ratio analysis (e.g., Debt/GDP).
- **YoY vs Index**: Prioritize `YoY` for growth charts. If only `Index` is available, note that `data_transformer` will need to calculate growth.

## 4. GEM-Specific Naming & Proactive Patterns
GEM series follow a strict colon-separated structure:
`Category: Sub-category: Frequency: Country`

**Proactive Pattern Matcher**:
1. Search for `[Metric]: [Sub-category]: [Frequency]: [Country A]`.
2. Extract the prefix: `[Metric]: [Sub-category]: [Frequency]:`.
3. Use the prefix to find `[Prefix] [Country B]`, `[Prefix] [Country C]`, etc.

Examples:
- `Real GDP: YoY: Quarterly: Indonesia`
- `Consumer Price Index: YoY: Monthly: Philippines`
- `Exports: fob: Monthly: Malaysia`

Run the Prepared Food CPI geopolitical price shock scenario analysis.

**Pre-check:** Verify `output/data/cpi_forecast/cpi_forecast_monthly.csv` exists. If not, tell the user to run `/cpi-forecast` first.

**Confirm with the user:**
1. Oil shock price (default: $128.78/bbl — Iran war scenario)
2. Scaling/dampening multiplier (default: 1.5x dampened pass-through)
3. Shock duration in months (default: 6 months)

**Then execute:**
```powershell
& '.venv\Scripts\python.exe' 'src\pipeline\prepared_food_shock\run_analysis.py'
```

**Outputs produced:**
- `output/data/prepared_food_shock/prepared_food_shock_comparison.csv`
- `output/chart/prepared_food_shock/` — baseline vs. shock charts
- `report/prepared_food_shock/prepared_food_shock.md` — scenario report

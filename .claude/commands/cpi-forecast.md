Run the Thailand CPI component forecasting pipeline.

**Pre-check:** Verify `output/data/energy_price_forecast/dubai_oil_forecast_production.csv` exists. If not, tell the user to run `/energy-forecast` first.

**Confirm with the user:**
- Forecast horizon (default: same as energy forecast)
- Any special CPI component to focus on, or run all 17 components (default)

**Then execute:**
```powershell
& 'bin\python.ps1' 'src\pipeline\cpi_forecast\orchestrator.py'
```

**Outputs produced:**
- `output/data/cpi_forecast/cpi_forecast_monthly.csv`
- `output/data/cpi_forecast/cpi_forecast_quarterly.csv`
- `output/data/cpi_forecast/cpi_forecast_annual.csv`
- `output/chart/cpi_forecast/` — component charts
- `report/cpi_forecast/cpi_forecast.md` — report

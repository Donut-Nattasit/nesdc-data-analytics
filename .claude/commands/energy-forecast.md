Run the Dubai Crude Oil price forecasting pipeline.

**Before running, confirm with the user:**
1. Forecast horizon (default: December of next year)
2. Whether `input/pipeline/dubai_oil/dubai_price.xlsx` has been updated with the latest actuals

**Then execute:**
```powershell
& '.venv\Scripts\python.exe' 'src\pipeline\energy_price_forecast\orchestrator.py'
```

**Outputs produced:**
- `output/data/energy_price_forecast/dubai_oil_master.csv` — historical master
- `output/data/energy_price_forecast/dubai_oil_forecast_production.csv` — forecast
- `output/chart/energy_price_forecast/` — 3 charts
- `report/energy_price_forecast/energy_price_forecast.md` — report

After pipeline completes, ask: "Would you like to continue to /cpi-forecast? (It depends on the Dubai oil output just produced.)"

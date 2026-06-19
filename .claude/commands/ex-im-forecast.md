Run the Export & Import Price Index forecasting pipeline.

**Pre-check:** Verify `output/data/energy_price_forecast/dubai_oil_forecast_production.csv` exists. If not, tell the user to run `/energy-forecast` first.

**Confirm with the user:**
- Forecast horizon (default: end of next year)
- Whether to run all components or a specific subset

**Then execute:**
```powershell
& 'bin\python.ps1' 'src\pipeline\ex_im_price_forecast\orchestrator.py'
```

**Outputs produced:**
- `output/data/ex_im_price_forecast/export_import_price_forecast_monthly.csv`
- `output/data/ex_im_price_forecast/export_import_price_forecast_quarterly.csv`
- `output/data/ex_im_price_forecast/export_import_price_forecast_annual.csv`
- `output/chart/ex_im_price_forecast/` — charts
- `report/ex_im_price_forecast/ex_im_price_forecast.md` — report

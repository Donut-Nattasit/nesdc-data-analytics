Run the Long-Range Energy Price Forecast (2–3 year horizon).

**Pre-checks:**
1. Verify `input/oil_price_forecast_LR/` contains an updated Excel scenario file
2. Verify `output/data/prepared_food_shock/prepared_food_shock_comparison.csv` exists

**Confirm with the user:**
- Which scenario file to use (list files in `input/oil_price_forecast_LR/`)
- Forecast end year (default: 2031)

**Then execute:**
```powershell
& '.venv\Scripts\python.exe' 'src\pipeline\energy_price_forecast_LR\orchestrator.py'
```

**Outputs produced:**
- `output/data/energy_price_forecast_LR/` — long-range forecast CSVs
- `output/chart/energy_price_forecast_LR/` — charts
- `report/energy_price_forecast_LR/energy_price_forecast_LR.md` — report

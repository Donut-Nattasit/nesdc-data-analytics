Run the Thailand Price System Forecast — the umbrella pipeline that assembles all sub-pipeline outputs into a unified report.

This command does NOT re-run sub-pipelines. It assembles their existing outputs.

**Required inputs (check all exist before proceeding):**
- `output/data/energy_price_forecast/dubai_oil_forecast_production.csv`
- `output/data/cpi_forecast/cpi_forecast_monthly.csv`
- `output/data/ex_im_price_forecast/export_import_price_forecast_quarterly.csv`

**If any input is missing**, tell the user which sub-pipeline to run first:
- Missing energy output → run `/energy-forecast`
- Missing CPI output → run `/cpi-forecast`
- Missing ex/im output → run `/ex-im-forecast`

**Confirm with the user:**
- Report period (default: latest available quarter)
- Whether to include food shock scenario in the synthesis

**Then execute:**
```powershell
& 'bin\python.ps1' 'src\pipeline\thailand_price_system\orchestrator.py'
```

**Outputs produced:**
- `output/data/thailand_price_system/thailand_price_system_monthly.csv`
- `output/data/thailand_price_system/thailand_price_system_quarterly.csv`
- `output/chart/thailand_price_system/` — synthesis charts
- `report/thailand_price_system/thailand_price_system.md` — integrated report

*Note: Deflator forecast (Phase 4) will be added once `deflator_forecast` pipeline is built.*

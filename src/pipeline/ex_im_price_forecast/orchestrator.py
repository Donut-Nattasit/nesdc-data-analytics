import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from src.pipeline.ex_im_price_forecast import (
    prepare_data,
    plot_charts,
    forecast_statsforecast,
    forecast_exogenous,
    aggregate_and_plot,
    resample_forecasts
)
from src.pipeline.base_orchestrator import run_steps


def main():
    print("======================================================================")
    print("    NESDC EXPORT & IMPORT PRICE ANALYSIS & FORECAST PIPE ORCHESTRATOR")
    print("======================================================================")

    project_root = Path(__file__).resolve().parent.parent.parent.parent
    print(f"Project Root: {project_root}")

    steps = [
        {"name": "Data Preparation & Ingestion", "func": prepare_data.main},
        {"name": "Historical Charts & Contributions", "func": plot_charts.main},
        {"name": "StatsForecast Baseline Models", "func": forecast_statsforecast.main},
        {"name": "ARIMAX/ARDL Exogenous Projections (Dubai Oil)", "func": forecast_exogenous.main},
        {"name": "Composite Aggregation & BOT Projection", "func": aggregate_and_plot.main},
        {"name": "Quarterly/Annual Resampling & Report Update", "func": resample_forecasts.main},
    ]

    run_steps(steps)

    print("\n======================================================================")
    print("                    PIPELINE COMPLETED SUCCESSFULLY")
    print("======================================================================")
    print("   Primary Artifacts:")
    print("   - data   : output/data/ex_im_price_forecast/")
    print("   - charts : output/chart/ex_im_price_forecast/")
    print("   - report : report/ex_im_price_forecast/ex_im_price_forecast.md")


if __name__ == "__main__":
    main()

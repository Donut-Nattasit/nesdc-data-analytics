import sys
import json
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from src.pipeline.energy_price_forecast import (
    prepare_data,
    predict_model,
    viz_global_prices,
    viz_dubai_situation,
    viz_dubai_forecast,
    generate_report
)
from src.pipeline.base_orchestrator import run_steps


def main():
    print("======================================================================")
    print("      NESDC DUBAI OIL ANALYSIS & FORECAST PIPE ORCHESTRATOR")
    print("======================================================================")

    project_root = Path(__file__).resolve().parent.parent.parent.parent
    print(f"Project Root: {project_root}")

    steps = [
        {"name": "Data Preparation & EIA Ingestion", "func": prepare_data.main},
        {"name": "Engle-Granger ECM Engine", "func": predict_model.main},
        {"name": "Global Price Benchmarks Chart", "func": viz_global_prices.main},
        {"name": "Dubai Spot Situation Chart", "func": viz_dubai_situation.main},
        {"name": "Dubai Forecast Comparison Chart", "func": viz_dubai_forecast.main},
        {"name": "Special Economic Report Compiler", "func": generate_report.main},
    ]

    run_steps(steps)

    print("\n======================================================================")
    print("                    PIPELINE COMPLETED SUCCESSFULLY")
    print("======================================================================")
    print("   Primary Artifacts:")
    print("   - data    : output/data/energy_price_forecast/dubai_oil_master.csv")
    print("   - forecast: output/data/energy_price_forecast/dubai_oil_forecast_production.csv")
    print("   - charts  : output/chart/energy_price_forecast/")
    print("   - report  : report/energy_price_forecast/energy_price_forecast.md")

    state_path = project_root / "PROJECT_STATE.json"
    if state_path.exists():
        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        last_report = state.get("reports", [])[-1] if state.get("reports") else {}
        print(f"\n   Registry: [{last_report.get('title', 'N/A')} — {last_report.get('status', 'N/A')}]")


if __name__ == "__main__":
    main()

import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(str(Path(__file__).resolve().parents[3]))

from src.pipeline.cpi_forecast import prepare_data, predict_model, generate_charts, generate_report
from src.pipeline.base_orchestrator import run_steps


def main():
    print("==========================================================")
    print("      NESDC Thailand CPI Forecasting Pipeline Orchestrator")
    print("==========================================================")
    start_time = time.time()

    steps = [
        {"name": "Data Acquisition & Transformation", "func": prepare_data.main},
        {"name": "Component Forecasting & Aggregation", "func": predict_model.main},
        {"name": "Chart Generation", "func": generate_charts.main},
        {"name": "Report Generation", "func": generate_report.main},
    ]

    run_steps(steps)

    duration = time.time() - start_time
    print("\n==========================================================")
    print(f"[OK] Pipeline completed in {duration:.1f} seconds.")
    print("   Charts  : output/chart/cpi_forecast/")
    print("   Report  : report/cpi_forecast/cpi_forecast.md")
    print("   Registry: PROJECT_STATE.json updated")
    print("==========================================================")


if __name__ == "__main__":
    main()

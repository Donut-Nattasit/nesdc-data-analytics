import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(str(Path(__file__).resolve().parents[3]))

from src.pipeline.energy_price_forecast_LR import prepare_data, predict_model, generate_charts, generate_report
from src.pipeline.base_orchestrator import run_steps

def main():
    print("==========================================================")
    print("      NESDC Energy Price Forecast — Long Range (LR)")
    print("==========================================================")
    start_time = time.time()

    steps = [
        {"name": "Data Ingestion & Seeding", "func": prepare_data.main},
        {"name": "Long-Range Forecasting & Aggregation", "func": predict_model.main},
        {"name": "Chart Generation", "func": generate_charts.main},
        {"name": "Report Generation (Long-Range Scenario)", "func": generate_report.main},
    ]

    run_steps(steps)

    duration = time.time() - start_time
    print("\n==========================================================")
    print(f"[OK] Pipeline completed in {duration:.1f} seconds.")
    print("   Charts  : output/chart/energy_price_forecast_LR/")
    print("   Report  : report/energy_price_forecast_LR/energy_price_forecast_LR.md")
    print("==========================================================")

if __name__ == "__main__":
    main()

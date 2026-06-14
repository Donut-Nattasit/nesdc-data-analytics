import os
import sys
import time
from pathlib import Path

# Override print to automatically flush stdout for background log visibility
_print = print
def print(*args, **kwargs):
    _print(*args, **kwargs)
    sys.stdout.flush()

# Add project root to sys.path to allow src imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

def main():
    print("==========================================================")
    print("      NESDC Thailand CPI Forecasting Pipeline Orchestrator")
    print("==========================================================")
    start_time = time.time()

    # 1. Run Data Preparation / Ingestion
    print("\n>>> Phase 1: Data Acquisition & Transformation")
    try:
        from src.pipeline.cpi_forecast.prepare_data import main as run_prep
        run_prep()
    except Exception as e:
        print(f"\n[FAIL] Pipeline failed during Phase 1 (Data Prep): {e}")
        raise RuntimeError("Pipeline step failed")

    # 2. Run Forecasting & Aggregation
    print("\n>>> Phase 2: Component Forecasting & Aggregation")
    try:
        from src.pipeline.cpi_forecast.predict_model import main as run_forecast
        run_forecast()
    except Exception as e:
        print(f"\n[FAIL] Pipeline failed during Phase 2 (Forecasting): {e}")
        raise RuntimeError("Pipeline step failed")

    # 3. Generate Composite / Component Line Charts
    print("\n>>> Phase 3: Chart Generation (Composite & Component Lines)")
    try:
        from src.pipeline.cpi_forecast.generate_charts import main as run_charts
        run_charts()
    except Exception as e:
        print(f"\n[FAIL] Pipeline failed during Phase 3 (Charts): {e}")
        raise RuntimeError("Pipeline step failed")

    # 4. Generate Full Report (all remaining charts + Markdown)
    print("\n>>> Phase 4: Report Generation")
    try:
        from src.pipeline.cpi_forecast.generate_report import main as run_report
        run_report()
    except Exception as e:
        print(f"\n[FAIL] Pipeline failed during Phase 4 (Report): {e}")
        raise RuntimeError("Pipeline step failed")

    duration = time.time() - start_time
    print("\n==========================================================")
    print(f"[OK] Full pipeline executed successfully in {duration:.1f} seconds.")
    print("  Outputs:")
    print("    Charts  : output/chart/cpi_forecast/")
    print("    Report  : report/cpi_forecast/cpi_forecast.md")
    print("    Registry: PROJECT_STATE.json updated")
    print("==========================================================")

if __name__ == "__main__":
    main()


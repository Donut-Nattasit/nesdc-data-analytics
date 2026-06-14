import os
import sys
import subprocess
from pathlib import Path
import json

# Enforce UTF-8 encoding for standard console output on Windows
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

def main():
    print("======================================================================")
    print("    NESDC EXPORT & IMPORT PRICE ANALYSIS & FORECAST PIPE ORCHESTRATOR")
    print("======================================================================")
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    print(f"Project Root: {project_root}")
    
    steps = [
        # Phase 1: Data Acquisition & Preprocessing
        {"name": "Data Preparation & Ingestion", "func": prepare_data.main},
        
        # Phase 2: Historical Asset Styling & Visualization
        {"name": "Historical Charts & Contributions", "func": plot_charts.main},
        
        # Phase 3: Rolling Window Validation & Baseline Forecasts
        {"name": "StatsForecast Baseline Models", "func": forecast_statsforecast.main},
        
        # Phase 4: Cointegration & Exogenous Model Calibration
        {"name": "ARIMAX/ARDL Exogenous Projections (Dubai Oil)", "func": forecast_exogenous.main},
        
        # Phase 5: Weight Aggregation & BOT Splicing
        {"name": "Composite Aggregation & BOT Projection", "func": aggregate_and_plot.main},
        
        # Phase 6: Volume-Weighted Resampling & Reporting
        {"name": "Quarterly/Annual Resampling & Report Update", "func": resample_forecasts.main}
    ]
    
    failed_steps = []
    
    for idx, step in enumerate(steps, 1):
        print(f"\n--- STEP {idx}/{len(steps)}: {step['name']} ---")
        try:
            step["func"]()
            print(f"✅ [Success] {step['name']}")
        except Exception as e:
            failed_steps.append(step["name"])
            print(f"\n⚠️ [Pipeline Alert] Step failed: {e}. Stopping pipeline.")
            import traceback
            traceback.print_exc()
            break
            
    print("\n======================================================================")
    print("                       PIPELINE RUN SUMMARY")
    print("======================================================================")
    if failed_steps:
        print(f"❌ PIPELINE RUN FAILED. Failed on step: {failed_steps[0]}")
        raise RuntimeError("Pipeline step failed")
    else:
        print("✅ PIPELINE RUN COMPLETED SUCCESSFULLY!")
        print("   Primary Artifacts Saved:")
        print("   - monthly dataset  : output/data/ex_im_price_forecast/export_import_price_monthly_wide.csv")
        print("   - quarterly dataset: output/data/ex_im_price_forecast/export_import_price_forecast_quarterly.csv")
        print("   - annual dataset   : output/data/ex_im_price_forecast/export_import_price_forecast_annual.csv")
        print("   - visual charts    : output/chart/ex_im_price_forecast/*.png")
        print("   - compiled report  : report/ex_im_price_forecast/ex_im_price_forecast.md")
        
        # Print registry update confirmation
        state_path = project_root / "PROJECT_STATE.json"
        if state_path.exists():
            with open(state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            # Find reports related to ex_im_price_forecast
            ex_im_reports = [r for r in state.get("reports", []) if "ex_im_price_forecast" in r.get("path", "")]
            if ex_im_reports:
                last_report = ex_im_reports[-1]
                print(f"\n📢 Manifest State Verified: [Report: '{last_report.get('title', 'N/A')}' (Status: {last_report.get('status', 'N/A')}, Date: {last_report.get('date', 'N/A')})]")

if __name__ == "__main__":
    main()

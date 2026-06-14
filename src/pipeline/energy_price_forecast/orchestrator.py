import os
import sys
import subprocess
from pathlib import Path
import json

# Enforce UTF-8 encoding for standard console output on Windows
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
from src.pipeline.cpi_forecast import orchestrator as cpi_orchestrator
from src.pipeline.prepared_food_shock import run_analysis as pfs_analysis
from src.pipeline.prepared_food_shock import generate_report as pfs_report

def main():
    print("======================================================================")
    print("      NESDC DUBAI OIL ANALYSIS & FORECAST PIPE ORCHESTRATOR")
    print("======================================================================")
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    
    print(f"Project Root: {project_root}")
    
    steps = [
        # Phase 1: Data Preparation & Ingestion
        {"name": "Data Preparation & EIA Ingestion", "func": prepare_data.main},
        
        # Phase 2: Model Estimation & Predictions
        {"name": "Engle-Granger ECM Engine", "func": predict_model.main},
        
        # Phase 3: Visual Assets Generation
        {"name": "Global Price Benchmarks Chart", "func": viz_global_prices.main},
        {"name": "Dubai Spot Situation Chart", "func": viz_dubai_situation.main},
        {"name": "Dubai Forecast Comparison Chart", "func": viz_dubai_forecast.main},
        
        # Phase 3.5: Downstream CPI & Shock Projections
        {"name": "CPI Baseline Forecast Orchestrator", "func": cpi_orchestrator.main},
        {"name": "Prepared Food CPI Shock Simulation", "func": pfs_analysis.main},
        {"name": "Prepared Food CPI Shock Report", "func": pfs_report.main},
        
        # Phase 4: Report Synthesis
        {"name": "Special Economic Report Compiler", "func": generate_report.main}
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
        print("   - transformed data : output/data/energy_price_forecast/dubai_oil_master.csv")
        print("   - forecast data    : output/data/energy_price_forecast/dubai_oil_forecast_production.csv")
        print("   - visual charts    : output/chart/*.png")
        print("   - compiled report  : report/energy_price_forecast/energy_price_forecast.md")
        
        # Print registry update confirmation
        state_path = project_root / "PROJECT_STATE.json"
        if state_path.exists():
            with open(state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            last_report = state.get("reports", [])[-1] if state.get("reports") else {}
            print(f"\n📢 Manifest State Verified: [Report: '{last_report.get('title', 'N/A')}' (Status: {last_report.get('status', 'N/A')}, Date: {last_report.get('date', 'N/A')})]")

if __name__ == "__main__":
    main()

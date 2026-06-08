import os
import sys
import subprocess
from pathlib import Path
import json

# Enforce UTF-8 encoding for standard console output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_script(script_path: Path, python_path: str, venv_python: Path) -> bool:
    """Run a python script in a clean subprocess with PYTHONPATH configured."""
    print(f"\n[Running] {script_path.name}...")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = python_path
    
    try:
        res = subprocess.run(
            [str(venv_python), str(script_path)],
            env=env,
            cwd=python_path,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if res.returncode == 0:
            print(f"✅ [Success] {script_path.name}")
            # Print last few lines of output
            lines = res.stdout.strip().split('\n')
            last_lines = [l for l in lines[-4:] if l]
            for l in last_lines:
                print(f"   > {l}")
            return True
        else:
            print(f"❌ [Failed] {script_path.name} (Exit code: {res.returncode})")
            print("--- Standard Error Output ---")
            print(res.stderr)
            print("--- Standard Output ---")
            print(res.stdout)
            return False
    except Exception as e:
        print(f"❌ [Exception] Failed to run {script_path.name}: {e}")
        return False

def main():
    print("======================================================================")
    print("    NESDC EXPORT & IMPORT PRICE ANALYSIS & FORECAST PIPE ORCHESTRATOR")
    print("======================================================================")
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    
    if not venv_python.exists():
        print(f"[Error] Virtual environment python not found at: {venv_python}")
        sys.exit(1)
        
    print(f"Project Root: {project_root}")
    print(f"Venv Python:  {venv_python}")
    
    pipeline_dir = project_root / "src" / "pipeline" / "ex_im_price_forecast"
    
    steps = [
        # Phase 1: Data Acquisition & Preprocessing
        {"name": "Data Preparation & Ingestion", "path": pipeline_dir / "prepare_data.py"},
        
        # Phase 2: Historical Asset Styling & Visualization
        {"name": "Historical Charts & Contributions", "path": pipeline_dir / "plot_charts.py"},
        
        # Phase 3: Rolling Window Validation & Baseline Forecasts
        {"name": "StatsForecast Baseline Models", "path": pipeline_dir / "forecast_statsforecast.py"},
        
        # Phase 4: Cointegration & Exogenous Model Calibration
        {"name": "ARIMAX/ARDL Exogenous Projections (Dubai Oil)", "path": pipeline_dir / "forecast_exogenous.py"},
        
        # Phase 5: Weight Aggregation & BOT Splicing
        {"name": "Composite Aggregation & BOT Projection", "path": pipeline_dir / "aggregate_and_plot.py"},
        
        # Phase 6: Volume-Weighted Resampling & Reporting
        {"name": "Quarterly/Annual Resampling & Report Update", "path": pipeline_dir / "resample_forecasts.py"}
    ]
    
    failed_steps = []
    
    for idx, step in enumerate(steps, 1):
        print(f"\n--- STEP {idx}/{len(steps)}: {step['name']} ---")
        success = run_script(step["path"], str(project_root), venv_python)
        if not success:
            failed_steps.append(step["name"])
            print("\n⚠️ [Pipeline Alert] Subprocess encountered an error. Stopping pipeline.")
            break
            
    print("\n======================================================================")
    print("                       PIPELINE RUN SUMMARY")
    print("======================================================================")
    if failed_steps:
        print(f"❌ PIPELINE RUN FAILED. Failed on step: {failed_steps[0]}")
        sys.exit(1)
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

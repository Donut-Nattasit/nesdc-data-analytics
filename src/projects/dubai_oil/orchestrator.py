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
        # Run standard python command
        res = subprocess.run(
            [str(venv_python), str(script_path)],
            env=env,
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
    print("      NESDC DUBAI OIL ANALYSIS & FORECAST PIPE ORCHESTRATOR")
    print("======================================================================")
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    
    if not venv_python.exists():
        print(f"[Error] Virtual environment python not found at: {venv_python}")
        sys.exit(1)
        
    print(f"Project Root: {project_root}")
    print(f"Venv Python:  {venv_python}")
    
    # Define scripts to run in order
    steps = [
        # Phase 1: Data Preparation & Ingestion
        {"name": "Data Preparation & EIA Ingestion", "path": project_root / "src" / "projects" / "dubai_oil" / "prepare_data.py"},
        
        # Phase 2: Model Estimation & Predictions
        {"name": "Engle-Granger ECM Engine", "path": project_root / "src" / "projects" / "dubai_oil" / "predict_model.py"},
        
        # Phase 3: Visual Assets Generation
        {"name": "Global Price Benchmarks Chart", "path": project_root / "src" / "projects" / "dubai_oil" / "viz_global_prices.py"},
        {"name": "Dubai Spot Situation Chart", "path": project_root / "src" / "projects" / "dubai_oil" / "viz_dubai_situation.py"},
        {"name": "Dubai Forecast Comparison Chart", "path": project_root / "src" / "projects" / "dubai_oil" / "viz_dubai_forecast.py"},
        
        # Phase 4: Report Synthesis
        {"name": "Special Economic Report Compiler", "path": project_root / "src" / "projects" / "dubai_oil" / "generate_report.py"}
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
        print("   - transformed data : output/dubai_oil/data/transformed/dubai_oil_master.csv")
        from datetime import datetime
        current_yyyy_mm = datetime.now().strftime('%Y-%m')
        print("   - forecast data    : output/dubai_oil/data/forecast/dubai_oil_forecast_production.csv")
        print("   - visual charts    : output/dubai_oil/chart/*.png (4 charts total)")
        print(f"   - compiled report  : output/report/price_forecast/{current_yyyy_mm}/01_dubai_price.md")
        
        # Print registry update confirmation
        state_path = project_root / ".gemini" / "PROJECT_STATE.json"
        if state_path.exists():
            with open(state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            last_report = state.get("reports", [])[-1] if state.get("reports") else {}
            print(f"\n📢 Manifest State Verified: [Report: '{last_report.get('title', 'N/A')}' (Status: {last_report.get('status', 'N/A')}, Date: {last_report.get('date', 'N/A')})]")

if __name__ == "__main__":
    main()

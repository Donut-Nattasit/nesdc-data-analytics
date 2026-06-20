"""
Deflator Prediction Pipeline - Orchestrator.

Runs the GDP deflator forecasting pipeline end-to-end:
  1. prepare_data   - fetch CEIC deflator + assemble quarterly exogenous frame
  2. predict_model  - log-log auto-ARIMAX forecast to 2027-Q4 + diagnostics

Charts (viz-expert) and the report (report-writer) are produced by the
respective NESDC sub-agents and are not re-run here.

Usage:
  $env:PYTHONPATH='.'; .\bin\python.ps1 src/pipeline/deflator_prediction/orchestrator.py
"""
from src.pipeline.deflator_prediction import prepare_data, predict_model
from src.pipeline.base_orchestrator import run_steps


def main():
    steps = [
        {"name": "Data Preparation", "func": prepare_data.main},
        {"name": "Model Prediction", "func": predict_model.main},
    ]
    run_steps(steps)

    print("\nPIPELINE COMPLETED SUCCESSFULLY")
    print("Primary Artifacts:")
    print("   - data    : output/data/deflator_prediction/deflator_forecast_quarterly.csv")
    print("   - data    : output/data/deflator_prediction/deflator_forecast_annual.csv")
    print("   - summary : output/model_summary/deflator_prediction/*.txt")
    print("   - charts  : output/chart/deflator_prediction/ (via viz-expert)")
    print("   - report  : report/deflator_prediction/deflator_prediction.md (via report-writer)")


if __name__ == "__main__":
    main()

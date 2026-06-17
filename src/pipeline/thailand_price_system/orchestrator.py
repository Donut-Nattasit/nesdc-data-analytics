"""
Thailand Price System Forecast — Umbrella Orchestrator

This orchestrator does NOT re-run sub-pipelines.
It reads their outputs and generates the integrated synthesis report.

Run order for sub-pipelines (managed by /thailand-price-system command):
  1. /energy-forecast
  2. /cpi-forecast
  3. /ex-im-forecast
  4. /food-shock (optional)
  5. /deflator-forecast (planned)
  6. This orchestrator
"""
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.pipeline.base_orchestrator import run_steps
from src.pipeline.thailand_price_system import generate_synthesis


REQUIRED_INPUTS = {
    "Dubai Oil Forecast":     "output/data/energy_price_forecast/dubai_oil_forecast_production.csv",
    "CPI Monthly Forecast":   "output/data/cpi_forecast/cpi_forecast_monthly.csv",
    "CPI Quarterly Forecast": "output/data/cpi_forecast/cpi_forecast_quarterly.csv",
    "Ex/Im Price Quarterly":  "output/data/ex_im_price_forecast/export_import_price_forecast_quarterly.csv",
}


def check_inputs() -> None:
    missing = [
        f"  - {name}: {path}"
        for name, path in REQUIRED_INPUTS.items()
        if not (ROOT / path).exists()
    ]
    if missing:
        raise FileNotFoundError(
            "Required sub-pipeline outputs missing. Run the relevant pipelines first:\n"
            + "\n".join(missing)
        )


def main() -> None:
    print("======================================================================")
    print("      NESDC THAILAND PRICE SYSTEM FORECAST — UMBRELLA ORCHESTRATOR")
    print("======================================================================")

    check_inputs()

    steps = [
        {"name": "Thailand Price System Synthesis", "func": generate_synthesis.main},
    ]

    run_steps(steps)

    print("\n======================================================================")
    print("                    PIPELINE COMPLETED SUCCESSFULLY")
    print("======================================================================")
    print("   Outputs:")
    print("   - data   : output/data/thailand_price_system/")
    print("   - report : report/thailand_price_system/thailand_price_system.md")
    print("   - charts : output/chart/thailand_price_system/")


if __name__ == "__main__":
    main()

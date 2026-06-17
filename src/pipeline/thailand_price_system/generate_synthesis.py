"""
Thailand Price System — Synthesis Generator

Reads outputs from all sub-pipelines and produces:
  - Merged wide-format CSVs (monthly + quarterly)
  - Multi-panel Markdown report
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]


def _load_if_exists(path: Path) -> pd.DataFrame:
    if path.exists():
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        return df
    return pd.DataFrame()


def main() -> None:
    config_path = ROOT / "src/pipeline/thailand_price_system/config/pipeline_config.json"
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    # ── Load sub-pipeline outputs ──────────────────────────────────────────────
    dubai = _load_if_exists(ROOT / config["required_inputs"]["Dubai Oil Forecast"])
    cpi_m = _load_if_exists(ROOT / config["required_inputs"]["CPI Monthly Forecast"])
    cpi_q = _load_if_exists(ROOT / config["required_inputs"]["CPI Quarterly Forecast"])
    exim_m = _load_if_exists(ROOT / config["required_inputs"]["Ex/Im Price Monthly"])
    exim_q = _load_if_exists(ROOT / config["required_inputs"]["Ex/Im Price Quarterly"])

    # ── Monthly synthesis ──────────────────────────────────────────────────────
    frames_m = [df for df in [dubai, cpi_m, exim_m] if not df.empty]
    if frames_m:
        synthesis_m = pd.concat(frames_m, axis=1, join="outer")
        synthesis_m.index.name = "date"
        out_m = ROOT / config["outputs"]["synthesis_monthly"]
        out_m.parent.mkdir(parents=True, exist_ok=True)
        synthesis_m.to_csv(out_m)
        print(f"[OK] Monthly synthesis: {out_m.relative_to(ROOT)}")

    # ── Quarterly synthesis ────────────────────────────────────────────────────
    frames_q = [df for df in [cpi_q, exim_q] if not df.empty]
    if frames_q:
        synthesis_q = pd.concat(frames_q, axis=1, join="outer")
        synthesis_q.index.name = "date"
        out_q = ROOT / config["outputs"]["synthesis_quarterly"]
        synthesis_q.to_csv(out_q)
        print(f"[OK] Quarterly synthesis: {out_q.relative_to(ROOT)}")

    # ── Registry update ────────────────────────────────────────────────────────
    import sys
    sys.path.insert(0, str(ROOT))
    from src.utils.registry import add_dataset
    add_dataset(
        series_id="Thailand Price System Synthesis",
        source="All sub-pipelines",
        transformed_path=str(out_m.relative_to(ROOT)) if frames_m else "",
        status="Ready",
    )
    print("[OK] Registry updated.")


if __name__ == "__main__":
    main()

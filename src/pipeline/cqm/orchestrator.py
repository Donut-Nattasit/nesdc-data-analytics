r"""
CQM orchestrator — wires the whole Current Quarterly Model nowcast end to end.

  fetch (CEIC)  ->  monthly indicator X13 SA + auto_arima forecast  ->
  bridge-equation OLS + identity solve  ->  GDP aggregation  ->  QoQ-saar / YoY tables.

Outputs (under the `cqm` pipeline namespace):
  output/data/cqm/nipa_forecast_levels.csv     full NIPA frame (actual + forecast)
  output/data/cqm/cqm_growth_quarterly.csv     key aggregates, YoY & QoQ-saar
  output/data/cqm/cqm_growth_annual.csv        annual YoY
  output/model_summary/cqm/cqm_run_summary.txt diagnostics (bridge R², fallbacks)

Run:  & '.\bin\python.ps1' 'src\pipeline\cqm\orchestrator.py'
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.pipeline.cqm.bridge_model import (BridgeEngine, apply_identities,
                                           univariate_forecast_levels)
from src.pipeline.cqm.config import load_config, project_root

OUT_DATA = project_root() / "output" / "data" / "cqm"
OUT_SUMMARY = project_root() / "output" / "model_summary" / "cqm"

INDUSTRY_CODES = ["010", "020", "030", "040", "050", "060", "070", "080", "090",
                  "100", "110", "120", "130", "140", "150", "160", "170", "180",
                  "190", "200"]

# key reporting aggregates: label -> (real, nominal)
REPORT = {
    "GDP (production)":      ("GDP_real", "GDP_nom"),
    "Private Consumption":  ("YRS010", "YNS010"),
    "Govt Consumption":     ("YRS020", "YNS020"),
    "Gross Fixed Capital":  ("YRS030", "YNS030"),
    "Exports G&S":          ("YRS060", "YNS060"),
    "Imports G&S":          ("YRS070", "YNS070"),
    "Agriculture":          ("ZRS010", "ZNS010"),
    "Manufacturing":        ("ZRS030", "ZNS030"),
    "Construction":         ("ZRS060", "ZNS060"),
    "Wholesale & Retail":   ("ZRS070", "ZNS070"),
    "Accom. & Food":        ("ZRS090", "ZNS090"),
    "Transport":            ("ZRS080", "ZNS080"),
}


def _ensure_forecast(nipa, engine):
    """Make sure every industry + expenditure leaf has a forecast (univariate fill)."""
    cfg = engine.cfg
    leaves = ([f"ZRS{c}" for c in INDUSTRY_CODES] + [f"ZNS{c}" for c in INDUSTRY_CODES]
              + ["YRS010", "YNS010", "YRS020", "YRS030", "YNS030",
                 "YRS060", "YNS060", "YRS070", "YNS070"])
    leaves = [c for c in leaves if c in nipa.columns]
    nipa = univariate_forecast_levels(nipa, leaves, engine.last_actual_q, engine.fq_index)
    return apply_identities(nipa, cfg.identities)


def _aggregate_gdp(nipa, last_actual_q):
    """GDP = industry-sum, but level-anchored to the official chain-volume aggregate
    (ZRS1000 / ZNS1000) so history matches NESDC exactly and the forecast extends it
    by the model's industry-sum growth (removes the stable ~3% CVM chain residual)."""
    nipa = nipa.copy()
    r = [f"ZRS{c}" for c in INDUSTRY_CODES if f"ZRS{c}" in nipa.columns]
    n = [f"ZNS{c}" for c in INDUSTRY_CODES if f"ZNS{c}" in nipa.columns]
    sum_r, sum_n = nipa[r].sum(axis=1), nipa[n].sum(axis=1)

    def _anchor(official_col, comp_sum):
        if official_col not in nipa.columns:
            return comp_sum
        off = nipa[official_col].copy()
        base = off.get(last_actual_q)
        base_sum = comp_sum.get(last_actual_q)
        out = off.copy()
        fut = nipa.index > last_actual_q
        if pd.notna(base) and pd.notna(base_sum) and base_sum:
            out[fut] = base * comp_sum[fut] / base_sum
        return out

    nipa["GDP_real"] = _anchor("ZRS1000", sum_r)
    nipa["GDP_nom"] = _anchor("ZNS1000", sum_n)
    nipa["GDP_deflator"] = nipa["GDP_nom"] / nipa["GDP_real"] * 100
    return nipa


def _growth_table(nipa, last_actual_q):
    rows = []
    for label, (rc, nc) in REPORT.items():
        if rc not in nipa.columns:
            continue
        s = nipa[rc]
        yoy = s.pct_change(4, fill_method=None) * 100
        saar = ((s / s.shift(1)) ** 4 - 1) * 100
        for t in nipa.index:
            rows.append({"series": label, "quarter": f"{t.year}Q{t.quarter}",
                         "date": t, "level_real": s.get(t),
                         "yoy_pct": yoy.get(t), "qoq_saar_pct": saar.get(t),
                         "is_forecast": t > last_actual_q})
    return pd.DataFrame(rows)


def run(forecast_quarters: int = 1, save: bool = True) -> dict:
    """CQM is a current-quarter nowcaster: forecast_quarters defaults to 1 (the single
    quarter after the last actual GDP). Do not raise this for production nowcasts —
    multi-step projection is a separate model's job."""
    cfg = load_config()
    monthly = pd.read_csv(OUT_DATA / "monthly_indicators_raw.csv", index_col=0, parse_dates=True)
    nipa_raw = pd.read_csv(OUT_DATA / "nipa_quarterly_raw.csv", index_col=0, parse_dates=True)
    qframe = pd.read_csv(OUT_DATA / "indicators_quarterly_FQ.csv", index_col=0, parse_dates=True)

    engine = BridgeEngine(nipa_raw, qframe, cfg, max_forecast_quarters=forecast_quarters)
    engine.estimate()
    nipa_fc = engine.forecast()
    nipa_fc = _ensure_forecast(nipa_fc, engine)
    nipa_fc = _aggregate_gdp(nipa_fc, engine.last_actual_q)

    growth = _growth_table(nipa_fc, engine.last_actual_q)
    # annual table: complete calendar years only (a 1-quarter nowcast cannot fill a year)
    gnn = nipa_fc[["GDP_real", "GDP_nom"]].dropna()
    counts = gnn.resample("YE").size()
    annual = gnn.resample("YE").sum()[counts == 4]
    annual["GDP_real_yoy"] = annual["GDP_real"].pct_change() * 100
    annual["GDP_deflator"] = annual["GDP_nom"] / annual["GDP_real"] * 100
    annual.index = annual.index.year

    if save:
        OUT_DATA.mkdir(parents=True, exist_ok=True)
        OUT_SUMMARY.mkdir(parents=True, exist_ok=True)
        nipa_fc.to_csv(OUT_DATA / "nipa_forecast_levels.csv")
        growth.to_csv(OUT_DATA / "cqm_growth_quarterly.csv", index=False)
        annual.to_csv(OUT_DATA / "cqm_growth_annual.csv")
        _write_summary(engine, nipa_fc, growth)

    # console preview: GDP nowcast
    gdp = growth[growth["series"] == "GDP (production)"]
    fc = gdp[gdp["is_forecast"]]
    print("\n=== GDP nowcast / forecast (production side, real) ===")
    print(fc[["quarter", "yoy_pct", "qoq_saar_pct"]].to_string(index=False))
    return {"nipa": nipa_fc, "growth": growth, "annual": annual, "engine": engine}


def _write_summary(engine, nipa_fc, growth):
    lines = ["CQM run summary", "=" * 50,
             f"Last actual NIPA quarter: {engine.last_actual_q:%Y}Q{engine.last_actual_q.quarter}",
             f"Forecast quarters: {len(engine.fq_index)} "
             f"({engine.fq_index.min():%Y}Q{engine.fq_index.min().quarter} -> "
             f"{engine.fq_index.max():%Y}Q{engine.fq_index.max().quarter})",
             f"Bridge equations estimated: {len(engine.results)}",
             f"Univariate-fallback components: {len(set(b for b,_ in engine.fallback))}",
             "", "Bridge equation fit (R2):", "-" * 30]
    for name, r in sorted(engine.results.items(), key=lambda kv: -kv[1]["rsq"]):
        lines.append(f"  {name:18s} {r['base']:10s} R2={r['rsq']:.3f}  "
                     f"({len(r['terms'])} regressors)")
    lines += ["", "Univariate fallback (no usable bridge regressor):",
              "  " + ", ".join(sorted(set(b for b, _ in engine.fallback)))]
    (OUT_SUMMARY / "cqm_run_summary.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"Summary -> {OUT_SUMMARY / 'cqm_run_summary.txt'}")


if __name__ == "__main__":
    run()

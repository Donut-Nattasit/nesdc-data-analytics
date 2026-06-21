r"""
Prepare CQM reporting artifacts:
  1. output/data/cqm/report_elements.csv  — tidy per-element series (actual+forecast,
     level + YoY) with clean human labels, for viz-expert to chart.
  2. output/model_summary/cqm/bridge_summaries_readable.md — every estimated bridge
     equation as a readable regression table (human variable names, no CEIC codes),
     for the report appendix.

Run:  & '.\bin\python.ps1' 'src\pipeline\cqm\report_prep.py'
"""
from __future__ import annotations

import re
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.stattools import durbin_watson

from src.pipeline.cqm.config import load_config, project_root
from src.pipeline.cqm.forecast_indicators import _sa_varname
from src.pipeline.cqm.bridge_model import _resolve_atom, _resolve_term, apply_identities

OUT = project_root() / "output" / "data" / "cqm"
SUMM = project_root() / "output" / "model_summary" / "cqm"

# ---- clean human labels for GDP elements ----
PROD_LABEL = {
    "010": "Agriculture", "020": "Mining & Quarrying", "030": "Manufacturing",
    "040": "Electricity & Gas", "050": "Water Supply & Waste", "060": "Construction",
    "070": "Wholesale & Retail Trade", "080": "Transport & Storage",
    "090": "Accommodation & Food", "100": "Information & Communication",
    "110": "Financial & Insurance", "120": "Real Estate", "130": "Professional & Scientific",
    "140": "Administrative & Support", "150": "Public Admin & Defence", "160": "Education",
    "170": "Health & Social Work", "180": "Arts & Entertainment", "190": "Other Services",
    "200": "Household Activities",
}
EXP_LABEL = {
    "YRS010": "Private Consumption", "YRS020": "Government Consumption",
    "YRS030": "Gross Fixed Capital Formation", "YRS031": "  - Construction Investment",
    "YRS032": "  - Equipment Investment", "YRS060": "Exports of Goods & Services",
    "YRS070": "Imports of Goods & Services",
}
AGG_LABEL = {"GDP_real": "Real GDP (CVM)", "GDP_nom": "Nominal GDP",
             "GDP_deflator": "GDP Deflator"}


def label_for(code: str) -> str:
    if code in AGG_LABEL:
        return AGG_LABEL[code]
    if code in EXP_LABEL:
        return EXP_LABEL[code]
    m = re.match(r"^Z[NRP]S(\d+)$", code)
    if m and m.group(1) in PROD_LABEL:
        return PROD_LABEL[m.group(1)]
    return code


def indicator_name_map(cfg) -> dict[str, str]:
    """SA-variable name (e.g. X_TOKAJOK_SA) -> readable indicator name."""
    out = {}
    for i in cfg.indicators:
        nm = (i.name or i.rename).strip()
        nm = re.sub(r"^\(DC\)", "", nm).strip()
        out[_sa_varname(i)] = nm
    for d in cfg.derived:
        base = d.arima["base"] if d.arima and d.arima.get("base") else f"{d.name}_SA"
        out[base] = {"X_ECIFFOB": "CIF-FOB export spread",
                     "X_MCIFFOB": "CIF-FOB import spread",
                     "X_GCON": "Govt construction spend",
                     "X_GEQ": "Govt equipment spend"}.get(d.name, d.name)
    return out


def readable_term(term: str, indmap: dict, lblmap_fn) -> str:
    """Turn a regressor term into a human phrase."""
    def one(atom):
        m = re.match(r"^(D\d)?([A-Za-z_]\w*?)(?:_FQ|_3m_FQ)?(?:\(-(\d+)\))?$", atom)
        # crude base extraction
        a = atom
        pre = ""
        mm = re.match(r"^(D\d)(.+)$", a)
        if mm:
            pre = {"D1": "Δ", "D4": "ΔYoY "}.get(mm.group(1), mm.group(1) + " ")
            a = mm.group(2)
        lag = ""
        ml = re.search(r"\(-(\d+)\)$", a)
        if ml:
            lag = f" (lag {ml.group(1)})"; a = re.sub(r"\(-\d+\)$", "", a)
        avg = ""
        if a.endswith("_3m_FQ"):
            avg = " 3m-avg"; base = a[:-len("_3m_FQ")]
        elif a.endswith("_FQ"):
            base = a[:-len("_FQ")]
        else:
            base = a
        if base in indmap:
            return f"{pre}{indmap[base]}{avg}{lag}"
        # NIPA variable
        return f"{pre}{lblmap_fn(base)}{lag}"
    atoms = re.findall(r"(?:D\d)?[A-Za-z_]\w*(?:\(-\d+\))?", term)
    out = term
    for a in sorted(set(atoms), key=len, reverse=True):
        out = out.replace(a, one(a))
    return out.strip()


def build_elements(cfg):
    nipa = pd.read_csv(OUT / "nipa_forecast_levels.csv", index_col=0, parse_dates=True)
    nipa.index = pd.PeriodIndex(nipa.index, freq="Q").to_timestamp(how="end").normalize()
    raw = pd.read_csv(OUT / "nipa_quarterly_raw.csv", index_col=0, parse_dates=True)
    last_act = pd.PeriodIndex(raw.index, freq="Q").to_timestamp(how="end").normalize().max()

    codes = (list(AGG_LABEL) + [f"ZRS{c}" for c in PROD_LABEL] + list(EXP_LABEL))
    rows = []
    for code in codes:
        if code not in nipa.columns:
            continue
        s = nipa[code]
        yoy = s.pct_change(4, fill_method=None) * 100
        grp = ("Aggregate" if code in AGG_LABEL else
               "Expenditure" if code in EXP_LABEL else "Production")
        for t in nipa.index:
            if pd.isna(s.get(t)):
                continue
            rows.append({"code": code, "label": label_for(code), "group": grp,
                         "date": t.date(), "quarter": f"{t.year}Q{t.quarter}",
                         "level": round(float(s.get(t)), 1),
                         "yoy_pct": (None if pd.isna(yoy.get(t)) else round(float(yoy.get(t)), 2)),
                         "is_forecast": bool(t > last_act)})
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "report_elements.csv", index=False)
    print(f"report_elements.csv: {df.shape}, {df['code'].nunique()} elements, "
          f"last actual {last_act.date()}")
    return last_act


def build_summaries(cfg):
    nipa = pd.read_csv(OUT / "nipa_quarterly_raw.csv", index_col=0, parse_dates=True)
    nipa.index = pd.PeriodIndex(nipa.index, freq="Q").to_timestamp(how="end").normalize()
    nipa = apply_identities(nipa, cfg.identities)
    ind = pd.read_csv(OUT / "indicators_quarterly_FQ.csv", index_col=0, parse_dates=True)
    ind.index = pd.PeriodIndex(ind.index, freq="Q").to_timestamp(how="end").normalize()
    last_act = nipa.dropna(how="all").index.max()
    ind = ind.loc[:last_act]
    ns = {c: nipa[c] for c in nipa.columns}
    ns.update({c: ind[c] for c in ind.columns})
    indmap = indicator_name_map(cfg)

    lines = ["# Appendix — CQM Bridge-Equation Summaries (readable)", "",
             "Each estimated bridge equation regresses the quarter-on-quarter (Δ) or "
             "year-on-year (ΔYoY) change in a GDP component on the corresponding monthly "
             "indicator(s), aggregated to quarterly. Variable names are shown in plain "
             "language; the underlying CEIC codes are in the model config. "
             f"Estimation sample ends {last_act.year}Q{last_act.quarter}.", ""]
    diff_lbl = {1: "Δ (QoQ)", 4: "ΔYoY"}
    n_ok = 0
    for b in cfg.bridges:
        lhs = _resolve_atom(b["lhs"], ns, nipa.index)
        if lhs is None:
            continue
        cols, names = [], []
        for term in b["rhs"]:
            s = _resolve_term(term, ns, nipa.index)
            if s is not None:
                cols.append(s.rename(term)); names.append(term)
        if not cols:
            continue
        data = pd.concat([lhs.rename("_y"), pd.concat(cols, axis=1)], axis=1).dropna()
        if len(data) < 12:
            continue
        X = sm.add_constant(data[names], has_constant="add")
        m = sm.OLS(data["_y"], X).fit()
        dw = durbin_watson(m.resid)
        n_ok += 1
        dep = f"{diff_lbl.get(b['lhs_diff'], 'Δ')} {label_for(b['lhs_base'])}"
        lines.append(f"### {label_for(b['lhs_base'])}  (`{b['lhs_base']}`)")
        lines.append(f"**Dependent variable:** {dep}  ·  "
                     f"**R² = {m.rsquared:.3f}** · adj-R² = {m.rsquared_adj:.3f} · "
                     f"n = {int(m.nobs)} · Durbin–Watson = {dw:.2f}")
        lines.append("")
        lines.append("| Driver | Coef. | Std.Err | t | p-value |")
        lines.append("|---|---:|---:|---:|---:|")
        for term in ["const"] + names:
            if term not in m.params:
                continue
            drv = "Intercept" if term == "const" else readable_term(term, indmap, label_for)
            lines.append(f"| {drv} | {m.params[term]:.4f} | {m.bse[term]:.4f} | "
                         f"{m.tvalues[term]:.2f} | {m.pvalues[term]:.3f} |")
        lines.append("")
    (SUMM).mkdir(parents=True, exist_ok=True)
    (SUMM / "bridge_summaries_readable.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"bridge_summaries_readable.md: {n_ok} equations")


if __name__ == "__main__":
    cfg = load_config()
    build_elements(cfg)
    build_summaries(cfg)

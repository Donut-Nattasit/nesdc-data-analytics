r"""
Assemble the CQM nowcast report (Markdown) from the pipeline outputs: charts
(output/chart/cqm), growth tables, report elements, and the readable bridge-equation
summaries. Visualization-first; model summaries in the appendix.

CQM is a CURRENT-QUARTER nowcaster — the report focuses on the single quarter being
nowcast (the forecast quarters present in the data), not a multi-year projection.

Output: report/cqm/CQM_Nowcast_Report.md

Run:  & '.\bin\python.ps1' 'src\pipeline\cqm\build_report.py'
"""
from __future__ import annotations

import pandas as pd

from src.pipeline.cqm.config import project_root

ROOT = project_root()
OUT = ROOT / "output" / "data" / "cqm"
SUMM = ROOT / "output" / "model_summary" / "cqm"
REPORT_DIR = ROOT / "report" / "cqm"
CH = "../../output/chart/cqm"          # relative path from report/cqm/


def _fig(n, fname, caption):
    return f"![{caption}]({CH}/{fname})\n\n**Figure {n}: {caption}**\n"


def _qsort(quarters):
    return sorted(quarters, key=lambda q: (int(q[:4]), int(q[-1])))


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    g = pd.read_csv(OUT / "cqm_growth_quarterly.csv")
    el = pd.read_csv(OUT / "report_elements.csv")

    gdp = g[g["series"] == "GDP (production)"].set_index("quarter")
    fcq = _qsort(g.loc[g["is_forecast"], "quarter"].unique())   # forecast (nowcast) quarters
    nowq = fcq[0]                                                # the current-quarter nowcast

    # ---- headline numbers ----
    hl_rows = ["| Quarter | Real GDP YoY % | QoQ saar % |", "|---|---:|---:|"]
    for q in fcq:
        r = gdp.loc[q]
        hl_rows.append(f"| {q} | {r['yoy_pct']:.1f} | {r['qoq_saar_pct']:.1f} |")
    hl_tbl = "\n".join(hl_rows)

    nfc = gdp.loc[nowq]
    summary = (
        f"The Current Quarterly Model nowcasts **Thailand real GDP growth of "
        f"{nfc['yoy_pct']:.1f}% YoY ({nfc['qoq_saar_pct']:.1f}% QoQ annualised) in {nowq}** "
        f"— the current quarter, for which official GDP has not yet been released. "
        f"The estimate is built bottom-up from 20 production sectors and the expenditure "
        f"components, driven by monthly activity indicators (industrial production, tourism, "
        f"trade, retail) that are seasonally adjusted and ARIMA-extended to complete the "
        f"quarter, then mapped to GDP through bridge equations."
    )

    # ---- forecast YoY by element ----
    def pivot(group):
        sub = el[(el["group"] == group) & (el["quarter"].isin(fcq))]
        p = sub.pivot_table(index="label", columns="quarter", values="yoy_pct")
        return p.reindex(columns=[q for q in fcq if q in p.columns])

    def tbl(p):
        cols = list(p.columns)
        head = "| Component | " + " | ".join(f"{c} YoY %" for c in cols) + " |"
        sep = "|---|" + "|".join(["---:"] * len(cols)) + "|"
        body = ["| " + lab.strip() + " | " +
                " | ".join(f"{r[c]:.1f}" if pd.notna(r[c]) else "–" for c in cols) + " |"
                for lab, r in p.iterrows()]
        return "\n".join([head, sep] + body)

    prod_p, exp_p = pivot("Production"), pivot("Expenditure")

    summaries = (SUMM / "bridge_summaries_readable.md").read_text(encoding="utf-8")
    summaries = "\n".join(summaries.split("\n")[1:]).strip()   # drop its H1

    md = f"""# Thailand GDP Nowcast — Current Quarterly Model (CQM)

*NESDC · Current-quarter nowcast for **{nowq}** · monthly indicators through May 2026 ·
Model: CQM Python port*

> **Scope:** CQM is a **current-quarter nowcasting** model — it estimates GDP for the
> quarter in progress (one quarter ahead of the latest official GDP). It is **not** a
> multi-quarter forecaster; longer-horizon projections are produced by a separate model.

## Executive summary

{summary}

**Table 1: Real GDP nowcast — {nowq}**

{hl_tbl}

*Source: NESDC CQM (Python port); CEIC data.*

> **Reliability:** in a 17-quarter backtest (2022Q1–2026Q1) the model's current-quarter
> real-GDP nowcast achieved **RMSE 0.64 pp** (MAE 0.53 pp), about 40% better than naive
> random-walk (1.06 pp) or persistence (1.14 pp) benchmarks.

---

## 1. Headline GDP

{_fig(1, "gdp_headline.png", "Thailand Real GDP — level and YoY growth, history and current-quarter nowcast")}

---

## 2. GDP by production sector

The model nowcasts each of the 20 production sectors and sums them to GDP. Trade,
manufacturing, tourism-related services (accommodation & transport) and electricity carry
the most statistically reliable bridge relationships.

{_fig(2, "production_grid.png", "GDP by production sector — real gross value added, history and nowcast")}

{_fig(3, "production_yoy_grid.png", "GDP by production sector — YoY % growth, history and nowcast")}

**Table 2: Production sectors — {nowq} nowcast (YoY % growth)**

{tbl(prod_p)}

*Source: NESDC CQM (Python port); CEIC data.*

---

## 3. GDP by expenditure

{_fig(4, "expenditure_grid.png", "GDP by expenditure component — real, history and nowcast")}

**Table 3: Expenditure components — {nowq} nowcast (YoY % growth)**

{tbl(exp_p)}

*Source: NESDC CQM (Python port); CEIC data.*

---

## 4. Prices — GDP deflator

{_fig(5, "gdp_deflator.png", "GDP deflator and nominal vs real GDP, history and nowcast")}

> **Note:** the deflator (price) block is the weakest part of the current model — its
> bridge equations have little out-of-sample skill and should be treated as indicative
> only. Rebuilding the price block is the top item in the improvement plan.

---

## 5. Model quality at a glance

- **46 of 60 bridge equations** estimate; **24 have genuine out-of-sample skill** (notably
  exports/imports, manufacturing, accommodation, electricity, private consumption).
- **17 equations have no out-of-sample skill** — mostly sector deflators; flagged for rework.
- **4 components** (public construction & equipment investment, construction supply,
  financial sector) currently use a univariate placeholder pending the internal government
  investment data feed.

Full diagnostics: `output/model_summary/cqm/cqm_quality_report.md`.
Improvement plan: `docs/cqm/IMPROVEMENT_STRATEGY.md`.

---

## 6. Caveats

- **Government investment** uses a statistical placeholder until NESDC supplies the monthly
  construction/equipment disbursement series.
- **Seasonal adjustment** currently uses full-sample X13 (a mild future peek); a real-time
  concurrent adjustment is planned.
- **Deflator / price** nowcasts are indicative only (see §4).
- **Scope:** current quarter only — this model does not produce multi-quarter forecasts.

---

## Appendix A — Nowcast tables ({nowq}, YoY % growth)

### A.1 Production sectors

{tbl(prod_p)}

### A.2 Expenditure components

{tbl(exp_p)}

*Source: NESDC CQM (Python port); CEIC data.*

---

## Appendix B — Bridge-equation summaries

{summaries}
"""
    path = REPORT_DIR / "CQM_Nowcast_Report.md"
    path.write_text(md, encoding="utf-8")
    print(f"Report written -> {path} ({len(md):,} chars). Nowcast quarter: {nowq}")


if __name__ == "__main__":
    main()

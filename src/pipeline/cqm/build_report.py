r"""
Assemble the CQM v1 nowcast report (Markdown) from the pipeline outputs:
charts (output/chart/cqm), growth tables, report elements, and the readable
bridge-equation summaries. Visualization-first; model summaries in the appendix.

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

FC_ORDER = ["2026Q2", "2026Q3", "2026Q4", "2027Q1", "2027Q2", "2027Q3"]


def _fig(n, fname, caption):
    return f"![{caption}]({CH}/{fname})\n\n**Figure {n}: {caption}**\n"


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    g = pd.read_csv(OUT / "cqm_growth_quarterly.csv")
    el = pd.read_csv(OUT / "report_elements.csv")

    gdp = g[g["series"] == "GDP (production)"].set_index("quarter")
    fc = [q for q in FC_ORDER if q in gdp.index]

    # ---- headline numbers ----
    def row(q):
        r = gdp.loc[q]
        return f"| {q} | {r['yoy_pct']:.1f} | {r['qoq_saar_pct']:.1f} |"
    hl_tbl = "\n".join(["| Quarter | Real GDP YoY % | QoQ saar % |",
                        "|---|---:|---:|"] + [row(q) for q in fc])

    first, last = fc[0], fc[-1]
    summary = (
        f"The Current Quarterly Model nowcasts **Thailand real GDP growth of "
        f"{gdp.loc[first,'yoy_pct']:.1f}% YoY in {first}**, "
        f"{gdp.loc['2026Q3','yoy_pct']:.1f}% in 2026Q3 and "
        f"{gdp.loc['2026Q4','yoy_pct']:.1f}% in 2026Q4, easing toward ~2% through {last}. "
        f"The estimate is built bottom-up from 20 production sectors and the expenditure "
        f"components, driven by monthly activity indicators (industrial production, tourism, "
        f"trade, retail) that are seasonally adjusted and ARIMA-extended to complete each "
        f"quarter, then mapped to GDP through bridge equations."
    )

    # ---- forecast YoY by element (appendix A) ----
    def pivot(group):
        sub = el[(el["group"] == group) & (el["quarter"].isin(FC_ORDER))]
        p = sub.pivot_table(index="label", columns="quarter", values="yoy_pct")
        p = p.reindex(columns=[q for q in FC_ORDER if q in p.columns])
        return p

    def tbl(p):
        cols = list(p.columns)
        head = "| Component | " + " | ".join(cols) + " |"
        sep = "|---|" + "|".join(["---:"] * len(cols)) + "|"
        body = []
        for lab, r in p.iterrows():
            body.append("| " + lab.strip() + " | " +
                        " | ".join(f"{r[c]:.1f}" if pd.notna(r[c]) else "–" for c in cols) + " |")
        return "\n".join([head, sep] + body)

    prod_p, exp_p = pivot("Production"), pivot("Expenditure")

    summaries = (SUMM / "bridge_summaries_readable.md").read_text(encoding="utf-8")
    # strip the file's own H1 so it nests under the appendix heading
    summaries = "\n".join(summaries.split("\n")[1:]).strip()

    md = f"""# Thailand GDP Nowcast — Current Quarterly Model (CQM)

*NESDC · Forecast vintage: last actual 2026Q1, monthly indicators through May 2026 ·
Model: CQM Python port v1*

## Executive summary

{summary}

**Table 1: Real GDP nowcast — forecast quarters**

{hl_tbl}

*Source: NESDC CQM (Python port); CEIC data.*

> **Reliability:** in a 17-quarter backtest (2022Q1–2026Q1) the model's one-quarter-ahead
> real-GDP nowcast achieved **RMSE 0.64 pp** (MAE 0.53 pp), about 40% better than naive
> random-walk (1.06 pp) or persistence (1.14 pp) benchmarks. The near-term quarters
> (2026Q2–Q3) are the most reliable; longer horizons increasingly revert to trend.

---

## 1. Headline GDP

{_fig(1, "gdp_headline.png", "Thailand Real GDP — level and YoY growth, actual vs CQM forecast")}

Real GDP is projected to keep expanding through the forecast horizon, with growth
strongest in mid-2026 before easing toward its ~2% trend.

---

## 2. GDP by production sector

The model forecasts each of the 20 production sectors and sums them to GDP. Trade,
manufacturing, tourism-related services (accommodation & transport) and electricity carry
the most statistically reliable bridge relationships.

{_fig(2, "production_grid.png", "GDP by production sector — real gross value added, actual vs forecast")}

{_fig(3, "production_yoy_grid.png", "GDP by production sector — YoY % growth, actual vs forecast")}

**Table 2: Production sectors — forecast YoY % growth**

{tbl(prod_p)}

*Source: NESDC CQM (Python port); CEIC data.*

---

## 3. GDP by expenditure

{_fig(4, "expenditure_grid.png", "GDP by expenditure component — real, actual vs forecast")}

**Table 3: Expenditure components — forecast YoY % growth**

{tbl(exp_p)}

*Source: NESDC CQM (Python port); CEIC data.*

---

## 4. Prices — GDP deflator

{_fig(5, "gdp_deflator.png", "GDP deflator and nominal vs real GDP, actual vs forecast")}

> **Note:** the deflator (price) block is the weakest part of v1 — its bridge equations
> have little out-of-sample skill and should be treated as indicative only. Rebuilding the
> price block is the top item in the improvement plan.

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

## 6. Caveats (v1)

- **Government investment** uses a statistical placeholder until NESDC supplies the monthly
  construction/equipment disbursement series.
- **Seasonal adjustment** currently uses full-sample X13 (a mild future peek); a real-time
  concurrent adjustment is planned.
- **Deflator / price** forecasts are indicative only (see §4).
- Beyond ~2 quarters the forecast increasingly reverts to trend (no exogenous scenario yet).

---

## Appendix A — Forecast tables (YoY % growth, all elements)

### A.1 Production sectors

{tbl(prod_p)}

### A.2 Expenditure components

{tbl(exp_p)}

*Source: NESDC CQM (Python port); CEIC data. Forecast quarters 2026Q2–2027Q3.*

---

## Appendix B — Bridge-equation summaries

{summaries}
"""
    path = REPORT_DIR / "CQM_Nowcast_Report.md"
    path.write_text(md, encoding="utf-8")
    print(f"Report written -> {path} ({len(md):,} chars)")


if __name__ == "__main__":
    main()

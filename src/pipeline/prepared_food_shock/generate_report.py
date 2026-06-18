import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# Override print to automatically flush stdout
_print = print
def print(*args, **kwargs):
    _print(*args, **kwargs)
    sys.stdout.flush()

# Paths
ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(ROOT))

DATA_DIR = ROOT / "output" / "data" / "prepared_food_shock"
REPORT_DIR = ROOT / "report" / "prepared_food_shock"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("==========================================================")
    print("  NESDC Prepared Food CPI Shock Report Generation Script")
    print("==========================================================")
    
    csv_path = DATA_DIR / "prepared_food_shock_comparison.csv"
    if not csv_path.exists():
        print(f"[FAIL] Comparison dataset not found at: {csv_path}")
        print("Please run run_analysis.py first.")
        raise RuntimeError("Pipeline step failed")
        
    df = pd.read_csv(csv_path, index_col='date', parse_dates=True).sort_index()
    
    # Load annual growth dataset
    csv_annual_path = DATA_DIR / "prepared_food_shock_annual_growth.csv"
    if not csv_annual_path.exists():
        print(f"[FAIL] Annual growth dataset not found at: {csv_annual_path}")
        raise RuntimeError("Pipeline step failed")
        
    df_annual = pd.read_csv(csv_annual_path, index_col='year').sort_index()
    
    # Generate the Markdown report using a raw string template to avoid f-string escaping issues with LaTeX
    report_path = REPORT_DIR / "prepared_food_shock.md"
    
    # Prepare comparison table markdown for specific dates
    dates_to_show = ['2026-05-01', '2026-06-01', '2026-07-01', '2026-08-01', '2026-09-01', '2026-10-01', '2026-11-01', '2026-12-01', '2027-06-01', '2027-12-01']
    
    # Table 1: Prepared Food CPI
    t1_rows = []
    for d in dates_to_show:
        row = df.loc[d]
        t1_rows.append(
            f"| {pd.to_datetime(d).strftime('%b %Y')} "
            f"| {row['Prepared_Food_Index_baseline']:.2f} | {row['Prepared_Food_Index_shock']:.2f} | {row['Prepared_Food_Index_shock'] - row['Prepared_Food_Index_baseline']:+.2f} "
            f"| {row['Prepared_Food_YoY_baseline']:.2f}% | {row['Prepared_Food_YoY_shock']:.2f}% | {row['Prepared_Food_YoY_shock'] - row['Prepared_Food_YoY_baseline']:+.2f}ppt |"
        )
    table_1_content = "\n".join(t1_rows)
    
    # Table 2: Headline CPI
    t2_rows = []
    for d in dates_to_show:
        row = df.loc[d]
        t2_rows.append(
            f"| {pd.to_datetime(d).strftime('%b %Y')} "
            f"| {row['Headline_CPI_baseline']:.2f} | {row['Headline_CPI_shock']:.2f} | {row['Headline_CPI_shock'] - row['Headline_CPI_baseline']:+.2f} "
            f"| {row['Headline_YoY_baseline']:.2f}% | {row['Headline_YoY_shock']:.2f}% | {row['Headline_YoY_shock'] - row['Headline_YoY_baseline']:+.2f}ppt |"
        )
    table_2_content = "\n".join(t2_rows)
    
    # Table 3: Core CPI
    t3_rows = []
    for d in dates_to_show:
        row = df.loc[d]
        t3_rows.append(
            f"| {pd.to_datetime(d).strftime('%b %Y')} "
            f"| {row['Core_CPI_baseline']:.2f} | {row['Core_CPI_shock']:.2f} | {row['Core_CPI_shock'] - row['Core_CPI_baseline']:+.2f} "
            f"| {row['Core_YoY_baseline']:.2f}% | {row['Core_YoY_shock']:.2f}% | {row['Core_YoY_shock'] - row['Core_YoY_baseline']:+.2f}ppt |"
        )
    table_3_content = "\n".join(t3_rows)
    
    # Table 4: Annual Growth Rates (History & Forecasts)
    t4_rows = []
    for yr in df_annual.index:
        row = df_annual.loc[yr]
        year_str = str(yr)[:4]
        pf_base = row['Prepared_Food_Annual_YoY_baseline']
        pf_shock = row['Prepared_Food_Annual_YoY_shock']
        pf_diff = pf_shock - pf_base
        
        hl_base = row['Headline_Annual_YoY_baseline']
        hl_shock = row['Headline_Annual_YoY_shock']
        hl_diff = hl_shock - hl_base
        
        c_base = row['Core_Annual_YoY_baseline']
        c_shock = row['Core_Annual_YoY_shock']
        c_diff = c_shock - c_base
        
        t4_rows.append(
            f"| {year_str} "
            f"| {pf_base:.2f}% | {pf_shock:.2f}% | {pf_diff:+.2f}ppt "
            f"| {hl_base:.2f}% | {hl_shock:.2f}% | {hl_diff:+.2f}ppt "
            f"| {c_base:.2f}% | {c_shock:.2f}% | {c_diff:+.2f}ppt |"
        )
    table_4_content = "\n".join(t4_rows)
    
    template = r"""# Prepared Food Price Shock Scenario Analysis (Iran War Oil Spike)
**NESDC Special Economic Brief** | Date: {{DATE}}

## 1. Executive Summary

This special economic brief analyzes the potential non-linear price transmission from the recent **Iran war geopolitical oil price shock** to Thailand's domestic **Prepared Food CPI** index, and its subsequent pass-through to aggregate Headline and Core inflation.

Geopolitical escalations in March 2026 caused Dubai Crude spot prices to spike by **88.6% MoM** (from $68.27/bbl to $128.78/bbl). While standard univariate linear models (such as auto-ARIMA) project a smooth, linear upward trend for Prepared Food prices, historical evidence shows that major oil shocks trigger sharp, non-linear jumps due to rapid increases in transportation, logistics, agricultural input, and packaging costs.

Using a **1.5x Dampened Scaling** model calibrated on the 2022 Russia-Ukraine oil shock, we estimate:
* **Immediate Prepared Food Surge**: A sharp **6.49% MoM jump** in Prepared Food CPI in **June 2026** (the first forecast month), shifting the index level from `106.75` in May to `113.68`. Under baseline linear models, the index was projected to rise to only `107.21` (+0.43% MoM).
* **Peaking YoY Inflation**: Prepared Food YoY growth is projected to peak at **13.75% YoY** in **November 2026** (vs. baseline forecast of `4.00%`).
* **Substantial Headline Inflation Impact**: Headline CPI inflation jumps from a baseline forecast of **2.66% YoY** to **3.73% YoY** in June 2026 (+1.07ppt), peaking at **4.15% YoY** in November 2026 (vs. baseline `2.46%`, a +1.69ppt increase).
* **Core CPI Push**: Core inflation is pushed up by **0.26ppt** in the long term, finishing December 2027 at **1.04% YoY** (vs. baseline `0.78%`).

---

## 2. Methodology & Assumptions

Standard linear forecasting models fail to capture the asymmetric and non-linear "step-ups" characteristic of consumer food prices during energy crises. Food vendors and food processing companies typically hold prices constant during mild oil fluctuations, but execute sharp, discrete price hikes when oil prices cross psychological threshold levels (such as $100/bbl).

To capture this behavior, we implement a **Historical Analogy Calibration (Scenario Multiplier)**:
1. **Calibration Event**: The 2022 Russia-Ukraine oil price spike, where Dubai crude increased by **32.9%** (from $83.46/bbl to $110.89/bbl). This oil shock triggered an initial **4.32% MoM jump** in Prepared Food CPI within one month, followed by an 11-month persistent propagation period, accumulating an **8.70% total increase**.
2. **Dampened Scaling**: The March 2026 oil spike (+88.6% MoM to $128.78/bbl) represents a much larger nominal shock. However, domestic price controls on essential cooking ingredients (e.g., palm oil, sugar) and electricity subsidies prevent a purely linear transmission. We therefore apply a **1.5x scaling multiplier** to the 2022 shock profile (rather than a raw 2.7x linear multiplier).
3. **Shock Equation**:
   $$\text{MoM shock}_t = 1.5 \times \text{MoM change 2022}_{(t - t_{shock})}$$
   for $t$ from June 2026 to April 2027.
4. **Composites Re-aggregation**: Under the shock scenario, Headline and Core CPI are re-weighted at each monthly period using the official component weights:
   $$\text{CPI Aggregate}_t = \frac{\sum_c \text{Index}_{c, t} \times \text{Weight}_{c, t}}{\sum_c \text{Weight}_{c, t}}$$
   where $c$ represents the components in the respective group, substituting the shocked index for Prepared Food.

---

## 3. Visualizations

The non-linear transmission creates a distinct step-up in index levels and growth rates compared to the linear baseline model.

![Prepared Food CPI Index Level Scenario Comparison](../../output/chart/prepared_food_shock/prepared_food_index_comparison.png)
**Figure 1: Prepared Food CPI Index Level Scenario Comparison (2021–2027)**

---

![Prepared Food CPI YoY Growth Scenario Comparison](../../output/chart/prepared_food_shock/prepared_food_yoy_comparison.png)
**Figure 2: Prepared Food CPI YoY Growth Scenario Comparison (2021–2027)**

---

![Headline and Core CPI aggregate inflation impact](../../output/chart/prepared_food_shock/cpi_aggregates_yoy_comparison.png)
**Figure 3: Headline and Core CPI Aggregate Inflation Impact (YoY %)**

---

## 4. Scenario Comparison Tables

The following tables show the index levels and YoY growth rates under the Baseline and Shock scenarios.

**Table 1: Prepared Food CPI Scenario Comparison (Index & YoY)**
| Month | Baseline Index | Shock Index | Index Diff | Baseline YoY | Shock YoY | YoY Diff (ppt) |
|-------|----------------|-------------|------------|--------------|-----------|----------------|
{{TABLE_1}}

**Table 2: Headline CPI Inflation Impact (Index & YoY)**
| Month | Baseline Index | Shock Index | Index Diff | Baseline YoY | Shock YoY | YoY Diff (ppt) |
|-------|----------------|-------------|------------|--------------|-----------|----------------|
{{TABLE_2}}

**Table 3: Core CPI Inflation Impact (Index & YoY)**
| Month | Baseline Index | Shock Index | Index Diff | Baseline YoY | Shock YoY | YoY Diff (ppt) |
|-------|----------------|-------------|------------|--------------|-----------|----------------|
{{TABLE_3}}

**Table 4: Annual YoY Inflation Growth Scenario Comparison (History & Forecasts)**
| Year | Prepared Food Baseline | Prepared Food Shock | Prepared Food Diff | Headline Baseline | Headline Shock | Headline Diff | Core Baseline | Core Shock | Core Diff |
|------|------------------------|---------------------|--------------------|-------------------|----------------|---------------|---------------|------------|-----------|
{{TABLE_4}}

---

## 5. Policy Implications

1. **Second-Round Pass-Through Risks**: Prepared food has a heavy weight of **15.8%** in the total CPI basket. A large jump in this component directly drives headline inflation, potentially triggering wage-price spiral expectations.
2. **Subsidies & Interventions**: Direct interventions on raw food ingredients (wheat, meats) might be more cost-effective in dampening headline inflation than general energy subsidies, as food prices exhibit extreme downward rigidity once hiked.
3. **Monetary Policy Stance**: Although Core CPI (excluding energy and raw food) is impacted moderately (+0.26ppt), the Headline CPI breach of 4% YoY in late 2026 may prompt the central bank to maintain a restrictive policy rate.
"""

    report_md = template.replace("{{DATE}}", datetime.now().strftime('%B %d, %Y')) \
                        .replace("{{TABLE_1}}", table_1_content) \
                        .replace("{{TABLE_2}}", table_2_content) \
                        .replace("{{TABLE_3}}", table_3_content) \
                        .replace("{{TABLE_4}}", table_4_content)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
        
    print(f"[OK] Generated Markdown report: {report_path}")
    

if __name__ == "__main__":
    main()

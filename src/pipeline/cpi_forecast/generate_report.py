import os
import sys
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from pathlib import Path

# Override print for log visibility
_print = print
def print(*args, **kwargs):
    _print(*args, **kwargs)
    sys.stdout.flush()

warnings.filterwarnings("ignore")

# ── Path resolution ──────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[3]
DATA_DIR   = ROOT / "output" / "data"  / "cpi_forecast"
CHART_DIR  = ROOT / "output" / "chart" / "cpi_forecast"
MODEL_DIR  = ROOT / "output" / "model_summary" / "cpi_forecast"
REPORT_DIR = ROOT / "report" / "cpi_forecast"

CHART_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.append(str(ROOT))
from src.utils.registry import add_visualization, add_report

# ── Style constants ───────────────────────────────────────────────────────────
COMPOSITE_COLORS = {
    "Headline_CPI":  "#00109E",
    "Core_CPI":      "#60B1E7",
    "Raw_Food_CPI":  "#BFB997",
    "Energy_CPI":    "#FFA300",
}
COMPOSITE_LABELS = {
    "Headline_CPI": "Headline CPI",
    "Core_CPI":     "Core CPI",
    "Raw_Food_CPI": "Raw Food CPI",
    "Energy_CPI":   "Energy CPI",
}
COMPONENT_COLS = [
    "index_Rice_Flour_Cereal", "index_Meats_Poultry_Fish",
    "index_Eggs_Dairy_Products", "index_Vegetables_Fruits",
    "index_Seasoning_Condiments", "index_Non_Alcoholic_Beverages",
    "index_Sugar_Product", "index_Prepared_Food",
    "index_Apparel_Footwears", "index_Housing_Furnishing_ex_Utility",
    "index_Housing_Furnishing_Utility", "index_Medical_Personal_Care",
    "index_Transport_Communication_ex_Motor_Fuel",
    "index_Transport_Communication_Motor_Fuel",
    "index_Recreation_Reading_Education_Religion",
    "index_Tobacco_Alcoholic_Beverages",
]
COMPONENT_LABELS = {c: c.replace("index_", "").replace("_", " ") for c in COMPONENT_COLS}
COMPONENT_GROUPS = {
    "index_Rice_Flour_Cereal":                         "Raw Food",
    "index_Meats_Poultry_Fish":                        "Raw Food",
    "index_Eggs_Dairy_Products":                       "Raw Food",
    "index_Vegetables_Fruits":                         "Raw Food",
    "index_Seasoning_Condiments":                      "Core",
    "index_Non_Alcoholic_Beverages":                   "Core",
    "index_Sugar_Product":                             "Core",
    "index_Prepared_Food":                             "Core",
    "index_Apparel_Footwears":                         "Core",
    "index_Housing_Furnishing_ex_Utility":             "Core",
    "index_Housing_Furnishing_Utility":                "Energy",
    "index_Medical_Personal_Care":                     "Core",
    "index_Transport_Communication_ex_Motor_Fuel":     "Core",
    "index_Transport_Communication_Motor_Fuel":        "Energy",
    "index_Recreation_Reading_Education_Religion":     "Core",
    "index_Tobacco_Alcoholic_Beverages":               "Core",
}
GROUP_COLORS = {"Core": "#60B1E7", "Raw Food": "#BFB997", "Energy": "#FFA300"}

WEIGHT_COLS = [c.replace("index_", "weight_") for c in COMPONENT_COLS]

WATERMARK = "Source: CEIC API & NESDC auto_ARIMA Forecast Model"

def apply_style(ax):
    ax.grid(True, linestyle="--", alpha=0.25, color="#cccccc")
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")

def shade_forecast(ax, df_plot, forecast_col="is_forecast"):
    """Draw red dashed separator + grey shading for forecast region."""
    if forecast_col in df_plot.columns:
        fc_start = df_plot[df_plot[forecast_col] == 1].index.min()
    else:
        fc_start = pd.Timestamp("2026-06-01")
    if pd.isna(fc_start):
        return
    sep = fc_start - pd.Timedelta(days=15)
    ax.axvline(sep, color="#FFA300", linestyle="--", linewidth=1.2, alpha=0.8)
    ax.axvspan(sep, df_plot.index.max(), color="#f5f6fa", alpha=0.9, zorder=0)
    ylim = ax.get_ylim()
    y_pos = ylim[0] + (ylim[1] - ylim[0]) * 0.93
    ax.text(fc_start + pd.Timedelta(days=10), y_pos, "FORECAST",
            color="#FFA300", fontweight="bold", fontsize=9, alpha=0.8)

def save(fig, name, tight=True, rect=None):
    path = CHART_DIR / name
    if tight:
        if rect is not None:
            fig.tight_layout(rect=rect)
        elif fig._suptitle is not None:
            fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        else:
            fig.tight_layout()
    # Add watermark once at the bottom left of the figure outside the axes box
    fig.text(0.02, 0.015, WATERMARK, fontsize=7.5, color="#7f8c8d", alpha=0.7, ha="left")
    fig.savefig(path, dpi=180)
    plt.close(fig)
    print(f"  [OK] {name}")
    return path

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
def load_data():
    monthly   = pd.read_csv(DATA_DIR / "cpi_forecast_monthly.csv",
                            index_col="date", parse_dates=True).sort_index()
    quarterly = pd.read_csv(DATA_DIR / "cpi_forecast_quarterly.csv",
                            index_col="date", parse_dates=True).sort_index()
    annual    = pd.read_csv(DATA_DIR / "cpi_forecast_annual.csv",
                            index_col="date", parse_dates=True).sort_index()
    return monthly, quarterly, annual

# ─────────────────────────────────────────────────────────────────────────────
# CHART 1 — Executive Summary: Annual growth bar chart
# ─────────────────────────────────────────────────────────────────────────────
def chart_exec_annual_growth(annual):
    print("\n[1] Executive summary annual growth bar chart...")
    composites = ["Headline_CPI", "Core_CPI", "Raw_Food_CPI", "Energy_CPI"]
    df = annual[composites].pct_change() * 100
    years_hist = list(range(2021, 2026))
    years_fc   = [2026, 2027]
    df.index = df.index.year
    df_hist = df.loc[years_hist]
    df_fc   = df.loc[years_fc]

    fig, ax = plt.subplots(figsize=(13, 6), dpi=180)
    x = np.arange(len(composites))
    width = 0.12
    offsets_hist = np.linspace(-0.32, 0.08, len(years_hist))
    offsets_fc   = [0.22, 0.34]

    hist_colors = ["#cbd5e1", "#94a3b8", "#64748b", "#334155", "#00109E"]
    fc_colors   = ["#ffca80", "#FFA300"]

    handles = []
    for i, (yr, off) in enumerate(zip(years_hist, offsets_hist)):
        color = hist_colors[i]
        vals  = [df_hist.loc[yr, c] for c in composites]
        bars  = ax.bar(x + off, vals, width=width, color=color, label=str(yr), zorder=3)
        handles.append(mpatches.Patch(color=color, label=str(yr)))

    for i, (yr, off) in enumerate(zip(years_fc, offsets_fc)):
        color = fc_colors[i]
        vals  = [df_fc.loc[yr, c] for c in composites]
        bars  = ax.bar(x + off, vals, width=width, color=color,
                       label=f"{yr} (F)", hatch="//", edgecolor="white", zorder=3)
        handles.append(mpatches.Patch(facecolor=color, hatch="//",
                                      edgecolor="grey", label=f"{yr} (Forecast)"))

    ax.axhline(0, color="#7f8c8d", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([COMPOSITE_LABELS[c] for c in composites], fontsize=11)
    ax.set_ylabel("YoY Growth (%)", fontsize=11, fontweight="bold", color="#2c3e50")
    ax.set_title("Thailand CPI Annual Growth Rate — Historical & Forecast",
                 fontsize=13, fontweight="bold", pad=14, color="#2c3e50")
    ax.legend(handles=handles, loc="upper right", fontsize=8.5,
              frameon=True, facecolor="white", edgecolor="none", ncol=4)
    apply_style(ax)
    return save(fig, "chart_exec_annual_growth_bar.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 2 — Overview: Monthly index level (4-panel)
# ─────────────────────────────────────────────────────────────────────────────
def chart_overview_index(monthly):
    print("\n[2] Overview index level 4-panel...")
    composites = ["Headline_CPI", "Core_CPI", "Raw_Food_CPI", "Energy_CPI"]
    hist = monthly[monthly["is_forecast"] == 0].loc["2021":]

    fig, axes = plt.subplots(4, 1, figsize=(12, 14), dpi=180, sharex=True)
    fig.suptitle("Thailand CPI Monthly Index Level (2021–Latest Actual)",
                 fontsize=13, fontweight="bold", y=0.98, color="#2c3e50")

    for ax, col in zip(axes, composites):
        color = COMPOSITE_COLORS[col]
        ax.plot(hist.index, hist[col], color=color, linewidth=2)
        # Callout: last actual point
        last_idx = hist[col].dropna().index[-1]
        last_val = hist[col].dropna().iloc[-1]
        ax.annotate(f"{last_val:.1f}",
                    xy=(last_idx, last_val),
                    xytext=(10, 0), textcoords="offset points",
                    fontsize=8.5, color=color, fontweight="bold",
                    arrowprops=dict(arrowstyle="-", color=color, lw=0.8))
        ax.set_ylabel("Index (2023=100)", fontsize=9, color="#2c3e50")
        ax.set_title(COMPOSITE_LABELS[col], fontsize=10, fontweight="bold",
                     color=color, pad=6)
        apply_style(ax)

    axes[-1].xaxis.set_major_locator(mdates.YearLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[-1].xaxis.set_minor_locator(mdates.MonthLocator(interval=3))
    fig.autofmt_xdate(rotation=0, ha="center")
    return save(fig, "chart_overview_index_level.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 3 — Overview: Monthly YoY growth (4-panel)
# ─────────────────────────────────────────────────────────────────────────────
def chart_overview_yoy(monthly):
    print("\n[3] Overview YoY growth 4-panel...")
    composites = ["Headline_CPI", "Core_CPI", "Raw_Food_CPI", "Energy_CPI"]
    hist = monthly[monthly["is_forecast"] == 0].copy()
    hist_yoy = hist[composites].pct_change(12) * 100
    hist_yoy = hist_yoy.loc["2021":]

    fig, axes = plt.subplots(4, 1, figsize=(12, 14), dpi=180, sharex=True)
    fig.suptitle("Thailand CPI Monthly YoY Growth (%) (2021–Latest Actual)",
                 fontsize=13, fontweight="bold", y=0.98, color="#2c3e50")

    for ax, col in zip(axes, composites):
        color = COMPOSITE_COLORS[col]
        ser = hist_yoy[col].dropna()
        ax.plot(ser.index, ser, color=color, linewidth=2)
        ax.axhline(0, color="#7f8c8d", linewidth=0.7, linestyle="--")
        # Callout
        last_idx = ser.index[-1]
        last_val = ser.iloc[-1]
        ax.annotate(f"{last_val:+.2f}%",
                    xy=(last_idx, last_val),
                    xytext=(10, 0), textcoords="offset points",
                    fontsize=8.5, color=color, fontweight="bold",
                    arrowprops=dict(arrowstyle="-", color=color, lw=0.8))
        ax.set_ylabel("YoY (%)", fontsize=9, color="#2c3e50")
        ax.set_title(COMPOSITE_LABELS[col], fontsize=10, fontweight="bold",
                     color=color, pad=6)
        apply_style(ax)

    axes[-1].xaxis.set_major_locator(mdates.YearLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.autofmt_xdate(rotation=0, ha="center")
    return save(fig, "chart_overview_yoy_growth.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 4 — Weight Pie (latest actual month)
# ─────────────────────────────────────────────────────────────────────────────
def chart_weight_pie(monthly):
    print("\n[4] Weight pie chart...")
    hist = monthly[monthly["is_forecast"] == 0].copy()
    latest = hist.dropna(subset=WEIGHT_COLS, how="all").iloc[-1]

    # Aggregate to Core / Raw Food / Energy
    core_w = sum(latest[c.replace("index_","weight_")] for c in COMPONENT_COLS
                 if COMPONENT_GROUPS[c] == "Core" and not pd.isna(latest.get(c.replace("index_","weight_"), np.nan)))
    raw_w  = sum(latest[c.replace("index_","weight_")] for c in COMPONENT_COLS
                 if COMPONENT_GROUPS[c] == "Raw Food" and not pd.isna(latest.get(c.replace("index_","weight_"), np.nan)))
    ener_w = sum(latest[c.replace("index_","weight_")] for c in COMPONENT_COLS
                 if COMPONENT_GROUPS[c] == "Energy" and not pd.isna(latest.get(c.replace("index_","weight_"), np.nan)))

    sizes  = [core_w, raw_w, ener_w]
    labels = ["Core", "Raw Food", "Energy"]
    colors = [GROUP_COLORS[l] for l in labels]
    explode = (0.03, 0.03, 0.03)

    fig, ax = plt.subplots(figsize=(7, 7), dpi=180)
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, explode=explode,
        autopct=lambda p: f"{p:.1f}%", startangle=140,
        textprops={"fontsize": 12, "color": "#2c3e50"},
        pctdistance=0.75, wedgeprops=dict(edgecolor="white", linewidth=2))
    for at in autotexts:
        at.set_fontsize(11)
        at.set_fontweight("bold")
        at.set_color("white")
    ax.set_title(f"CPI Weight Composition — Latest Actual Month",
                 fontsize=12, fontweight="bold", color="#2c3e50", pad=16)
    ax.text(0, -1.25, WATERMARK, fontsize=7, color="#7f8c8d",
            ha="center", alpha=0.7)
    return save(fig, "chart_weight_pie.png", tight=False)

# ─────────────────────────────────────────────────────────────────────────────
# CHART 5 — Contribution to Growth: Composites stacked bar
# ─────────────────────────────────────────────────────────────────────────────
def chart_contribution_composite(monthly):
    print("\n[5] Contribution to growth — composite stacked bar...")
    hist = monthly[monthly["is_forecast"] == 0].copy()
    composites = ["Core_CPI", "Raw_Food_CPI", "Energy_CPI", "Headline_CPI"]
    df = hist[composites].pct_change(12) * 100
    df = df.loc["2021":].dropna()

    # Approximate contribution: weight_share * component_yoy
    # Use headline yoy and decompose via proportional attribution
    # (simple approach: scaled by average weight shares)
    weight_map = {"Core_CPI": "core", "Raw_Food_CPI": "raw", "Energy_CPI": "energy"}
    
    # Get latest weights
    latest = hist.dropna(subset=WEIGHT_COLS, how="all").iloc[-1]
    core_w = sum(latest.get(c.replace("index_","weight_"),0) for c in COMPONENT_COLS if COMPONENT_GROUPS[c]=="Core" and not pd.isna(latest.get(c.replace("index_","weight_"),np.nan)))
    raw_w  = sum(latest.get(c.replace("index_","weight_"),0) for c in COMPONENT_COLS if COMPONENT_GROUPS[c]=="Raw Food" and not pd.isna(latest.get(c.replace("index_","weight_"),np.nan)))
    ener_w = sum(latest.get(c.replace("index_","weight_"),0) for c in COMPONENT_COLS if COMPONENT_GROUPS[c]=="Energy" and not pd.isna(latest.get(c.replace("index_","weight_"),np.nan)))
    total_w = core_w + raw_w + ener_w

    contrib = pd.DataFrame(index=df.index)
    contrib["Core"]     = df["Core_CPI"]     * (core_w / total_w)
    contrib["Raw Food"] = df["Raw_Food_CPI"] * (raw_w  / total_w)
    contrib["Energy"]   = df["Energy_CPI"]   * (ener_w / total_w)

    fig, ax = plt.subplots(figsize=(13, 5.5), dpi=180)
    bottom_pos = np.zeros(len(contrib))
    bottom_neg = np.zeros(len(contrib))
    xs = contrib.index

    for grp in ["Core", "Raw Food", "Energy"]:
        vals = contrib[grp].values
        pos = np.where(vals > 0, vals, 0)
        neg = np.where(vals < 0, vals, 0)
        ax.bar(xs, pos, bottom=bottom_pos, color=GROUP_COLORS[grp],
               label=grp, width=20, zorder=3)
        ax.bar(xs, neg, bottom=bottom_neg, color=GROUP_COLORS[grp],
               width=20, zorder=3)
        bottom_pos += pos
        bottom_neg += neg

    ax.plot(xs, df["Headline_CPI"], color="#2c3e50", linewidth=2,
            label="Headline CPI (YoY)", zorder=5)
    ax.axhline(0, color="#7f8c8d", linewidth=0.8)
    ax.set_title("Contribution to Headline CPI Growth (YoY) by Group",
                 fontsize=13, fontweight="bold", pad=12, color="#2c3e50")
    ax.set_ylabel("Contribution (ppt)", fontsize=10, color="#2c3e50")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=3))
    ax.legend(loc="upper right", fontsize=9, frameon=True, facecolor="white",
              edgecolor="none")
    apply_style(ax)
    return save(fig, "chart_contribution_composite.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 6 — Contribution to Growth: Component stacked bar
# ─────────────────────────────────────────────────────────────────────────────
def chart_contribution_component(monthly):
    print("\n[6] Contribution to growth — component stacked bar...")
    hist = monthly[monthly["is_forecast"] == 0].copy()
    yoy_idx = hist[COMPONENT_COLS].pct_change(12) * 100
    yoy_idx = yoy_idx.loc["2021":].dropna()

    # Approximate contribution: index_yoy * weight_share
    latest = hist.dropna(subset=WEIGHT_COLS, how="all").iloc[-1]
    total_w = sum(latest.get(w, 0) for w in WEIGHT_COLS if not pd.isna(latest.get(w, np.nan)))

    contrib = pd.DataFrame(index=yoy_idx.index)
    for col in COMPONENT_COLS:
        w_col = col.replace("index_", "weight_")
        w = latest.get(w_col, 0)
        if pd.isna(w):
            w = 0
        contrib[col] = yoy_idx[col] * (w / total_w) if total_w > 0 else 0

    # 16-color distinct palette
    base_colors = [
        "#1abc9c","#2ecc71","#3498db","#9b59b6","#e67e22","#e74c3c",
        "#1a252f","#f39c12","#16a085","#8e44ad","#27ae60","#2980b9",
        "#d35400","#c0392b","#7f8c8d","#2c3e50",
    ]
    fig, ax = plt.subplots(figsize=(14, 6.5), dpi=180)
    bottom_pos = np.zeros(len(contrib))
    bottom_neg = np.zeros(len(contrib))
    xs = contrib.index
    handles = []
    for i, col in enumerate(COMPONENT_COLS):
        color = base_colors[i % len(base_colors)]
        vals  = contrib[col].values
        pos   = np.where(vals > 0, vals, 0)
        neg   = np.where(vals < 0, vals, 0)
        ax.bar(xs, pos, bottom=bottom_pos, color=color, width=20, zorder=3)
        ax.bar(xs, neg, bottom=bottom_neg, color=color, width=20, zorder=3)
        bottom_pos += pos
        bottom_neg += neg
        handles.append(mpatches.Patch(color=color, label=COMPONENT_LABELS[col]))

    hl_yoy = hist["Headline_CPI"].pct_change(12) * 100
    hl_yoy = hl_yoy.loc[yoy_idx.index]
    ax.plot(xs, hl_yoy, color="#00109E", linewidth=2, label="Headline", zorder=5)
    handles.insert(0, mpatches.Patch(color="#00109E", label="Headline CPI (YoY)"))
    ax.axhline(0, color="#7f8c8d", linewidth=0.8)
    ax.set_title("Contribution to Headline CPI Growth (YoY) by Component",
                 fontsize=13, fontweight="bold", pad=12, color="#2c3e50")
    ax.set_ylabel("Contribution (ppt)", fontsize=10, color="#2c3e50")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=7.5,
              frameon=True, facecolor="white", edgecolor="none", ncol=1)
    fig.subplots_adjust(right=0.78, bottom=0.15, left=0.08, top=0.9)
    apply_style(ax)
    return save(fig, "chart_contribution_component.png", tight=False)

# ─────────────────────────────────────────────────────────────────────────────
# CHART 7 — Forecast: Monthly YoY composite (Jan 2026 → Dec 2027)
# ─────────────────────────────────────────────────────────────────────────────
def chart_forecast_monthly_yoy(monthly):
    print("\n[7] Forecast monthly YoY composite...")
    composites = ["Headline_CPI", "Core_CPI", "Raw_Food_CPI", "Energy_CPI"]
    df_yoy = monthly[composites].pct_change(12) * 100
    df_yoy = df_yoy.loc["2026-01":"2027-12"]

    is_fc = monthly["is_forecast"].reindex(df_yoy.index)

    fig, ax = plt.subplots(figsize=(12, 6), dpi=180)
    for col in composites:
        color = COMPOSITE_COLORS[col]
        label = COMPOSITE_LABELS[col]
        ax.plot(df_yoy.index, df_yoy[col], color=color, linewidth=2, label=label)

    ax.axhline(0, color="#7f8c8d", linewidth=0.8)
    shade_forecast(ax, monthly.reindex(df_yoy.index))
    ax.set_title("Thailand CPI — Monthly YoY Growth Forecast (Jan 2026–Dec 2027)",
                 fontsize=13, fontweight="bold", pad=12, color="#2c3e50")
    ax.set_ylabel("YoY Growth (%)", fontsize=10, color="#2c3e50")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.legend(fontsize=9, frameon=True, facecolor="white", edgecolor="none")
    fig.autofmt_xdate(rotation=30)
    apply_style(ax)
    return save(fig, "chart_forecast_monthly_composite_yoy.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 8 — Forecast: Quarterly YoY composite
# ─────────────────────────────────────────────────────────────────────────────
def chart_forecast_quarterly_yoy(quarterly):
    print("\n[8] Forecast quarterly YoY composite...")
    composites = ["Headline_CPI", "Core_CPI", "Raw_Food_CPI", "Energy_CPI"]
    df_yoy = quarterly[composites].pct_change(4) * 100
    df_yoy = df_yoy.loc["2026":"2027"]

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=180)
    x = np.arange(len(df_yoy))
    width = 0.2
    offsets = [-0.3, -0.1, 0.1, 0.3]
    for col, off in zip(composites, offsets):
        ax.bar(x + off, df_yoy[col].values, width=width,
               color=COMPOSITE_COLORS[col], label=COMPOSITE_LABELS[col], zorder=3)

    ax.axhline(0, color="#7f8c8d", linewidth=0.8)
    xlabels = [f"Q{((d.month-1)//3)+1} {d.year}" for d in df_yoy.index]
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, fontsize=9)
    ax.set_title("CPI Quarterly YoY Growth Forecast (2026–2027)",
                 fontsize=13, fontweight="bold", pad=12, color="#2c3e50")
    ax.set_ylabel("YoY Growth (%)", fontsize=10, color="#2c3e50")
    ax.legend(fontsize=9, frameon=True, facecolor="white", edgecolor="none")
    apply_style(ax)
    return save(fig, "chart_forecast_quarterly_composite_yoy.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 9 — Forecast: Annual YoY composite bar
# ─────────────────────────────────────────────────────────────────────────────
def chart_forecast_annual_yoy(annual):
    print("\n[9] Forecast annual YoY composite...")
    composites = ["Headline_CPI", "Core_CPI", "Raw_Food_CPI", "Energy_CPI"]
    df_yoy = annual[composites].pct_change() * 100
    df_yoy = df_yoy.loc["2021":"2027"]
    df_yoy.index = df_yoy.index.year

    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=180)
    x = np.arange(len(df_yoy))
    width = 0.18
    offsets = [-0.27, -0.09, 0.09, 0.27]
    for col, off in zip(composites, offsets):
        vals  = df_yoy[col].values
        # Draw historical bars (solid) and forecast bars (semi-transparent) separately
        hist_mask = [yr < 2026 for yr in df_yoy.index]
        fc_mask   = [yr >= 2026 for yr in df_yoy.index]
        hist_x = x[hist_mask]
        fc_x   = x[fc_mask]
        hist_v = vals[hist_mask]
        fc_v   = vals[fc_mask]
        label_added = False
        if len(hist_x):
            ax.bar(hist_x + off, hist_v, width=width, color=COMPOSITE_COLORS[col],
                   label=COMPOSITE_LABELS[col], zorder=3)
            label_added = True
        if len(fc_x):
            ax.bar(fc_x + off, fc_v, width=width, color=COMPOSITE_COLORS[col],
                   alpha=0.55, hatch="//", edgecolor="white", zorder=3,
                   label=None if label_added else COMPOSITE_LABELS[col])

    # Forecast separator
    ax.axvline(4.5, color="#e74c3c", linestyle="--", linewidth=1.2, alpha=0.8)
    ax.axhline(0, color="#7f8c8d", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(df_yoy.index.tolist(), fontsize=10)
    # Annotate FORECAST after ylim is set by bars
    ylim = ax.get_ylim()
    ax.text(5.0, ylim[0] + (ylim[1] - ylim[0]) * 0.88, "FORECAST",
            color="#e74c3c", fontweight="bold", fontsize=9)
    ax.set_title("CPI Annual YoY Growth \u2014 History & Forecast (2021\u20132027)",
                 fontsize=13, fontweight="bold", pad=12, color="#2c3e50")
    ax.set_ylabel("YoY Growth (%)", fontsize=10, color="#2c3e50")
    ax.legend(fontsize=9, frameon=True, facecolor="white", edgecolor="none", ncol=2)
    apply_style(ax)
    return save(fig, "chart_forecast_annual_composite_yoy.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 10 — Appendix: Weight area (composite)
# ─────────────────────────────────────────────────────────────────────────────
def chart_appendix_weight_area_composite(monthly):
    print("\n[10] Appendix weight area — composite...")
    hist = monthly[monthly["is_forecast"] == 0].copy()
    # Compute group weight
    df = pd.DataFrame(index=hist.index)
    for grp in ["Core", "Raw Food", "Energy"]:
        cols = [c.replace("index_","weight_") for c in COMPONENT_COLS
                if COMPONENT_GROUPS[c] == grp]
        df[grp] = hist[[c for c in cols if c in hist.columns]].sum(axis=1)
    df = df.replace(0, np.nan).dropna(how="all").fillna(method="ffill")
    df = df.loc["2007":]

    fig, ax = plt.subplots(figsize=(12, 5), dpi=180)
    total = df.sum(axis=1).replace(0, np.nan)
    df_pct = df.div(total, axis=0) * 100

    ax.stackplot(df_pct.index,
                 [df_pct["Core"], df_pct["Raw Food"], df_pct["Energy"]],
                 labels=["Core", "Raw Food", "Energy"],
                 colors=[GROUP_COLORS["Core"], GROUP_COLORS["Raw Food"], GROUP_COLORS["Energy"]],
                 alpha=0.85)
    ax.set_ylim(0, 100)
    ax.set_title("CPI Weight Composition Over Time — Composite Groups",
                 fontsize=12, fontweight="bold", pad=12, color="#2c3e50")
    ax.set_ylabel("Share (%)", fontsize=10, color="#2c3e50")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="lower right", fontsize=9, frameon=True, facecolor="white", edgecolor="none")
    apply_style(ax)
    return save(fig, "chart_appendix_weight_area_composite.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 11 — Appendix: Weight area (component)
# ─────────────────────────────────────────────────────────────────────────────
def chart_appendix_weight_area_component(monthly):
    print("\n[11] Appendix weight area — component...")
    hist = monthly[monthly["is_forecast"] == 0].copy()
    w_cols = [c for c in WEIGHT_COLS if c in hist.columns]
    df_w = hist[w_cols].loc["2018-01-01":].replace(0, np.nan).dropna(how="all").fillna(method="ffill")
    total = df_w.sum(axis=1).replace(0, np.nan)
    df_pct = df_w.div(total, axis=0) * 100

    base_colors = [
        "#1abc9c","#2ecc71","#3498db","#9b59b6","#e67e22","#e74c3c",
        "#1a252f","#f39c12","#16a085","#8e44ad","#27ae60","#2980b9",
        "#d35400","#c0392b","#7f8c8d","#2c3e50",
    ]
    labels = [COMPONENT_LABELS[c.replace("weight_", "index_")] for c in w_cols]

    fig, ax = plt.subplots(figsize=(13, 6), dpi=180)
    ax.stackplot(df_pct.index,
                 [df_pct[c].values for c in w_cols],
                 labels=labels,
                 colors=base_colors[:len(w_cols)],
                 alpha=0.82)
    ax.set_ylim(0, 100)
    ax.set_title("CPI Weight Composition Over Time — All Components",
                 fontsize=12, fontweight="bold", pad=12, color="#2c3e50")
    ax.set_ylabel("Share (%)", fontsize=10, color="#2c3e50")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=7, frameon=True, facecolor="white",
              edgecolor="none", ncol=1)
    fig.subplots_adjust(right=0.78, bottom=0.15, left=0.08, top=0.9)
    apply_style(ax)
    return save(fig, "chart_appendix_weight_area_component.png", tight=False)

# ─────────────────────────────────────────────────────────────────────────────
# CHART 12 — Appendix: Component YoY multi-panel
# ─────────────────────────────────────────────────────────────────────────────
def chart_appendix_component_yoy(monthly):
    print("\n[12] Appendix component YoY multi-panel...")
    df_yoy = monthly[COMPONENT_COLS].pct_change(12) * 100
    df_yoy = df_yoy.loc["2021":]

    n = len(COMPONENT_COLS)
    ncols = 4
    nrows = (n + ncols - 1) // ncols
    base_colors = [
        "#1abc9c","#2ecc71","#3498db","#9b59b6","#e67e22","#e74c3c",
        "#1a252f","#f39c12","#16a085","#8e44ad","#27ae60","#2980b9",
        "#d35400","#c0392b","#7f8c8d","#2c3e50",
    ]
    fig, axes = plt.subplots(nrows, ncols, figsize=(16, nrows * 3.2), dpi=150)
    axes = axes.flatten()

    for i, col in enumerate(COMPONENT_COLS):
        ax = axes[i]
        color = base_colors[i]
        ser = df_yoy[col].dropna()
        ax.plot(ser.index, ser, color=color, linewidth=1.8)
        ax.axhline(0, color="#7f8c8d", linewidth=0.6, linestyle="--")
        ax.set_title(COMPONENT_LABELS[col], fontsize=8.5, fontweight="bold",
                     color=color, pad=4)
        ax.tick_params(labelsize=7)
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        for sp in ["top", "right"]:
            ax.spines[sp].set_visible(False)
        ax.grid(True, linestyle="--", alpha=0.2)

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle("CPI Component YoY Growth (%) — Monthly (2021–Forecast)",
                 fontsize=13, fontweight="bold", y=0.96, color="#2c3e50")
    fig.autofmt_xdate(rotation=30)
    return save(fig, "chart_appendix_component_yoy.png", rect=[0, 0.03, 1, 0.92])

# ─────────────────────────────────────────────────────────────────────────────
# CHART 13 — Appendix: Component Index Level multi-panel (with forecast)
# ─────────────────────────────────────────────────────────────────────────────
def chart_appendix_component_level(monthly):
    print("\n[13] Appendix component index level 4x4 multi-panel...")
    df_all = monthly[COMPONENT_COLS + ["is_forecast"]].loc["2021":].copy()

    n = len(COMPONENT_COLS)
    ncols = 4
    nrows = (n + ncols - 1) // ncols
    base_colors = [
        "#1abc9c","#2ecc71","#3498db","#9b59b6","#e67e22","#e74c3c",
        "#1a252f","#f39c12","#16a085","#8e44ad","#27ae60","#2980b9",
        "#d35400","#c0392b","#7f8c8d","#2c3e50",
    ]

    fig, axes = plt.subplots(nrows, ncols, figsize=(16, nrows * 3.2), dpi=150)
    axes = axes.flatten()

    fc_start = df_all[df_all["is_forecast"] == 1].index.min()

    for i, col in enumerate(COMPONENT_COLS):
        ax = axes[i]
        color = base_colors[i]
        ser = df_all[col].dropna()

        # Historical segment
        hist_ser = ser[ser.index < fc_start] if pd.notna(fc_start) else ser
        fc_ser   = ser[ser.index >= fc_start] if pd.notna(fc_start) else pd.Series(dtype=float)

        ax.plot(hist_ser.index, hist_ser, color=color, linewidth=1.8)
        if len(fc_ser):
            ax.plot(fc_ser.index, fc_ser, color=color, linewidth=1.8,
                    linestyle="--", alpha=0.85)
            # Shaded forecast region
            ax.axvspan(fc_start - pd.Timedelta(days=15),
                       ser.index.max(),
                       color="#f5f6fa", alpha=0.85, zorder=0)
            ax.axvline(fc_start - pd.Timedelta(days=15),
                       color="#e74c3c", linestyle="--", linewidth=0.8, alpha=0.7)

        ax.set_title(COMPONENT_LABELS[col], fontsize=8.5, fontweight="bold",
                     color=color, pad=4)
        ax.set_ylabel("Index (2023=100)", fontsize=6.5, color="#555")
        ax.tick_params(labelsize=7)
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        for sp in ["top", "right"]:
            ax.spines[sp].set_visible(False)
        ax.grid(True, linestyle="--", alpha=0.2)

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle("CPI Component Index Level — Monthly (2021–Forecast, dashed)",
                 fontsize=13, fontweight="bold", y=0.96, color="#2c3e50")
    fig.autofmt_xdate(rotation=30)
    return save(fig, "chart_appendix_component_level.png", rect=[0, 0.03, 1, 0.92])

# ─────────────────────────────────────────────────────────────────────────────
# TABLE BUILDERS
# ─────────────────────────────────────────────────────────────────────────────
def build_weight_table(monthly):
    hist = monthly[monthly["is_forecast"] == 0].copy()
    latest = hist.dropna(subset=WEIGHT_COLS, how="all").iloc[-1]
    latest_date = hist.dropna(subset=WEIGHT_COLS, how="all").index[-1]

    rows = []
    for col in COMPONENT_COLS:
        w_col = col.replace("index_", "weight_")
        w = latest.get(w_col, np.nan)
        if not pd.isna(w):
            rows.append({
                "Component": COMPONENT_LABELS[col],
                "Weight": round(w, 4),
                "Group": COMPONENT_GROUPS[col],
            })
    df_tbl = pd.DataFrame(rows).sort_values("Weight", ascending=False).reset_index(drop=True)
    return df_tbl, latest_date

def build_monthly_yoy_table(monthly):
    composites = ["Headline_CPI", "Core_CPI", "Raw_Food_CPI", "Energy_CPI"]
    df_yoy = monthly[composites + ["is_forecast"]].copy()
    df_yoy[composites] = df_yoy[composites].pct_change(12) * 100
    df_yoy = df_yoy.loc["2026-01":"2027-12"].dropna(subset=composites, how="all")
    df_out = df_yoy[composites].round(2)
    df_out.index = df_out.index.strftime("%b %Y")
    df_out.columns = ["Headline (%)", "Core (%)", "Raw Food (%)", "Energy (%)"]
    return df_out

def build_quarterly_yoy_table(quarterly):
    composites = ["Headline_CPI", "Core_CPI", "Raw_Food_CPI", "Energy_CPI"]
    df_yoy = quarterly[composites].pct_change(4) * 100
    df_yoy = df_yoy.loc["2026":"2027"].dropna(how="all").round(2)
    df_yoy.index = [f"Q{((d.month-1)//3)+1} {d.year}" for d in df_yoy.index]
    df_yoy.columns = ["Headline (%)", "Core (%)", "Raw Food (%)", "Energy (%)"]
    return df_yoy
def build_annual_yoy_table(annual):
    composites = ["Headline_CPI", "Core_CPI", "Raw_Food_CPI", "Energy_CPI"]
    df_yoy = annual[composites].pct_change() * 100
    df_yoy = df_yoy.loc["2021":"2027"].dropna(how="all").round(2)
    df_yoy.index = df_yoy.index.year
    df_yoy.columns = ["Headline (%)", "Core (%)", "Raw Food (%)", "Energy (%)"]
    return df_yoy

def build_component_tables(monthly, quarterly, annual):
    """Returns (monthly_df, quarterly_df, annual_df) for component YoY."""
    monthly_yoy   = monthly[COMPONENT_COLS].pct_change(12)  * 100
    quarterly_yoy = quarterly[COMPONENT_COLS].pct_change(4)  * 100
    annual_yoy    = annual[COMPONENT_COLS].pct_change()      * 100

    col_labels = {c: COMPONENT_LABELS[c] for c in COMPONENT_COLS}

    def _slice_and_label(df, start, end, date_fmt):
        df = df.loc[start:end].dropna(how="all").round(2)
        df.index = df.index.strftime(date_fmt)
        df.columns = [col_labels[c] for c in COMPONENT_COLS]
        return df

    m  = _slice_and_label(monthly_yoy,   "2026-01", "2027-12", "%b %Y")
    q  = _slice_and_label(quarterly_yoy, "2026",    "2027",    "%b %Y")
    a  = _slice_and_label(annual_yoy,    "2021",    "2027",    "%Y")
    a.index = [int(d) for d in a.index]
    return m, q, a

def df_to_md(df, float_fmt=".2f"):
    """Convert DataFrame to Markdown table string."""
    return df.to_markdown(floatfmt=float_fmt)

# ─────────────────────────────────────────────────────────────────────────────
# MODEL SUMMARY LOADER
# ─────────────────────────────────────────────────────────────────────────────
def load_model_summaries():
    summaries = {}
    for col in COMPONENT_COLS:
        fname = MODEL_DIR / f"{col}_summary.txt"
        if fname.exists():
            with open(fname, "r", encoding="utf-8") as f:
                summaries[COMPONENT_LABELS[col]] = f.read()
    return summaries

# ─────────────────────────────────────────────────────────────────────────────
# REPORT COMPILER
# ─────────────────────────────────────────────────────────────────────────────
def compile_report(monthly, quarterly, annual, chart_paths):
    print("\n[Compiling Markdown report...]")
    report_path = REPORT_DIR / "cpi_forecast.md"

    # ── Tables ──
    weight_tbl, latest_wt_date = build_weight_table(monthly)
    monthly_yoy_tbl   = build_monthly_yoy_table(monthly)
    quarterly_yoy_tbl = build_quarterly_yoy_table(quarterly)
    annual_yoy_tbl    = build_annual_yoy_table(annual)
    comp_m, comp_q, comp_a = build_component_tables(monthly, quarterly, annual)
    model_summaries = load_model_summaries()

    # Latest actual data point info
    hist = monthly[monthly["is_forecast"] == 0]
    latest_date  = hist.index.max()
    latest_hl    = hist.loc[latest_date, "Headline_CPI"]
    # Latest YoY
    if (latest_date - pd.DateOffset(months=12)) in hist.index:
        prev_hl = hist.loc[latest_date - pd.DateOffset(months=12), "Headline_CPI"]
        latest_yoy = (latest_hl / prev_hl - 1) * 100
    else:
        latest_yoy = float("nan")

    # Forecast highlights (annual 2026 & 2027)
    ann_yoy = annual[["Headline_CPI","Core_CPI","Raw_Food_CPI","Energy_CPI"]].pct_change() * 100
    hl_2026 = float(ann_yoy.loc[ann_yoy.index.year == 2026, "Headline_CPI"].iloc[0])
    hl_2027 = float(ann_yoy.loc[ann_yoy.index.year == 2027, "Headline_CPI"].iloc[0])

    def rel(png_name):
        return f"../../output/chart/cpi_forecast/{png_name}"

    md = f"""# Thailand CPI Forecasting Report

> **Pipeline**: `cpi_forecast` | **Forecast Horizon**: June 2026 – December 2027  
> **Source**: CEIC API (Thailand NSO CPI Data) | **Model**: auto-ARIMA / ARIMAX  
> **Generated**: {pd.Timestamp.now().strftime('%d %B %Y')}

---

## Executive Summary

As of **{latest_date.strftime('%B %Y')}**, Thailand's Headline CPI index stands at **{latest_hl:.2f}** (2023 = 100),
with a year-on-year growth rate of **{latest_yoy:+.2f}%**.

The NESDC auto-ARIMA model projects Headline CPI growth to **recover to {hl_2026:.2f}%** in 2026,
driven primarily by a temporary rebound in energy prices, before moderating to **{hl_2027:.2f}%** in 2027.
Core inflation is expected to remain subdued, staying within the 0.9–1.0% band over the forecast horizon.

**Table 1: Annual CPI YoY Growth — Historical (2021–2025) & Forecast (2026–2027)**

{df_to_md(annual_yoy_tbl)}

![Thailand CPI Annual Growth Bar Chart]({rel('chart_exec_annual_growth_bar.png')})
**Figure 1: Annual YoY Growth Rate by CPI Aggregate — Historical and Forecast**

---

## 1. CPI Overview

### 1.1 Monthly CPI Index Level

The following charts show the historical monthly CPI index levels for each composite
(2021–latest actual). All indices are rebased to 2023 = 100.

![CPI Monthly Index Level]({rel('chart_overview_index_level.png')})
**Figure 2: Thailand CPI Monthly Index Level by Composite (2021–Latest Actual, 2023 = 100)**

### 1.2 Monthly YoY Growth

![CPI Monthly YoY Growth]({rel('chart_overview_yoy_growth.png')})
**Figure 3: Thailand CPI Monthly Year-on-Year Growth (%) by Composite (2021–Latest Actual)**

---

### 1.3 CPI Weight Composition

The pie chart below shows the share of each composite group in the total CPI basket,
based on the most recent available weights (as of **{latest_wt_date.strftime('%B %Y')}**).

![CPI Weight Pie Chart]({rel('chart_weight_pie.png')})
**Figure 4: CPI Weight Composition — Core, Raw Food, and Energy (Latest Month)**

**Table 2: CPI Component Weights — Sorted by Share (Latest Month)**

{df_to_md(weight_tbl)}

---

### 1.4 Contribution to Growth

The following charts decompose the Headline CPI's YoY growth into contributions from
each composite group and individual component.

![Contribution to Growth — Composite]({rel('chart_contribution_composite.png')})
**Figure 5: Contribution to Headline CPI YoY Growth by Group (Core / Raw Food / Energy)**

![Contribution to Growth — Component]({rel('chart_contribution_component.png')})
**Figure 6: Contribution to Headline CPI YoY Growth by Individual Component**

---

## 2. CPI Forecasting

### 2.1 Monthly Forecast

The component-level monthly forecast charts are provided in **Appendix B**.
The charts below focus on the composite-level monthly forecast.

![Monthly Forecast — Composite YoY]({rel('chart_forecast_monthly_composite_yoy.png')})
**Figure 7: Monthly CPI YoY Growth Forecast — Headline, Core, Raw Food, Energy (Jan 2026–Dec 2027)**

**Table 3: Monthly CPI YoY Growth Forecast (Jan 2026–Dec 2027)**

{df_to_md(monthly_yoy_tbl)}

---

### 2.2 Quarterly Forecast

![Quarterly Forecast — Composite YoY]({rel('chart_forecast_quarterly_composite_yoy.png')})
**Figure 8: Quarterly CPI YoY Growth Forecast — Composite Aggregates (2026–2027)**

**Table 4: Quarterly CPI YoY Growth Forecast (2026–2027)**

{df_to_md(quarterly_yoy_tbl)}

---

### 2.3 Annual Forecast

![Annual Forecast — Composite YoY]({rel('chart_forecast_annual_composite_yoy.png')})
**Figure 9: Annual CPI YoY Growth — Historical and Forecast (2021–2027)**

**Table 5: Annual CPI YoY Growth — Historical and Forecast (2021–2027)**

{df_to_md(annual_yoy_tbl)}

---

## Appendix

### Appendix A: CPI Weight Changes Over Time

![Weight Area — Composite]({rel('chart_appendix_weight_area_composite.png')})
**Figure 10: 100% Area Chart — CPI Weight by Composite Group Over Time**

![Weight Area — Component]({rel('chart_appendix_weight_area_component.png')})
**Figure 11: 100% Area Chart — CPI Weight by Individual Component Over Time**

---

### Appendix B: CPI and Growth by Component

![Component Level]({rel('chart_appendix_component_level.png')})
**Figure 12: Monthly CPI Index Level by Component (2021–Forecast, dashed line = forecast)**

![Component YoY]({rel('chart_appendix_component_yoy.png')})
**Figure 13: YoY Growth (%) by Individual CPI Component — Monthly (2021–Forecast)**

**Table 6: Monthly Component YoY Growth (%) — Jan 2026 to Dec 2027**

{df_to_md(comp_m)}

**Table 7: Quarterly Component YoY Growth (%) — 2026 to 2027**

{df_to_md(comp_q)}

**Table 8: Annual Component YoY Growth (%) — 2021 to 2027**

{df_to_md(comp_a)}

---

### Appendix C: Model Summary by Component

"""
    for comp_name, summary in model_summaries.items():
        md += f"#### {comp_name}\n\n```\n{summary}\n```\n\n"

    md += "\n---\n*Report generated by NESDC CPI Forecasting Pipeline (`src/pipeline/cpi_forecast/`)*\n"

    report_path.write_text(md, encoding="utf-8")
    print(f"  [OK] Report saved: {report_path}")
    return report_path

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  CPI Forecast Report Generator")
    print("=" * 60)

    monthly, quarterly, annual = load_data()

    chart_paths = {}
    chart_paths["exec_annual"]              = chart_exec_annual_growth(annual)
    chart_paths["overview_index"]           = chart_overview_index(monthly)
    chart_paths["overview_yoy"]             = chart_overview_yoy(monthly)
    chart_paths["weight_pie"]               = chart_weight_pie(monthly)
    chart_paths["contribution_composite"]   = chart_contribution_composite(monthly)
    chart_paths["contribution_component"]   = chart_contribution_component(monthly)
    chart_paths["forecast_monthly_yoy"]     = chart_forecast_monthly_yoy(monthly)
    chart_paths["forecast_quarterly_yoy"]   = chart_forecast_quarterly_yoy(quarterly)
    chart_paths["forecast_annual_yoy"]      = chart_forecast_annual_yoy(annual)
    chart_paths["appendix_weight_comp"]     = chart_appendix_weight_area_composite(monthly)
    chart_paths["appendix_weight_ind"]      = chart_appendix_weight_area_component(monthly)
    chart_paths["appendix_component_yoy"]   = chart_appendix_component_yoy(monthly)
    chart_paths["appendix_component_level"]  = chart_appendix_component_level(monthly)

    report_path = compile_report(monthly, quarterly, annual, chart_paths)

    print("\n[Registering in PROJECT_STATE.json...]")
    for key, path in chart_paths.items():
        try:
            rel_path = str(path.relative_to(ROOT)).replace("\\", "/")
            add_visualization(
                name=f"CPI Forecast — {key.replace('_', ' ').title()}",
                chart_type="Mixed",
                source_data="output/data/cpi_forecast/",
                png_path=rel_path,
                status="Rendered"
            )
        except Exception as e:
            print(f"  [Warn] Could not register {key}: {e}")
    try:
        rel_report = str(report_path.relative_to(ROOT)).replace("\\", "/")
        add_report(
            title="Thailand CPI Forecasting Report",
            author="Chief Economist",
            path=rel_report,
            status="Published"
        )
        print("  [OK] Report registered.")
    except Exception as e:
        print(f"  [Warn] Could not register report: {e}")

    print("\n" + "=" * 60)
    print("[DONE] All charts and report generated successfully.")
    print("=" * 60)

if __name__ == "__main__":
    main()

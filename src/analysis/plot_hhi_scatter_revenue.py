"""
plot_hhi_scatter_revenue.py
------------------------------
@viz_expert — Scatter plot variant:
  Y-axis  : HHI (Herfindahl-Hirschman Index)
  X-axis  : Total Revenue (log scale, THB)
  Color   : TSIC Category section (A, B, C, ...)

Styling: FC Vision theme via src/visualization/charts.py
Output : output/chart/hhi_scatter_revenue.png
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

from src.visualization.charts import configure_matplotlib_font
configure_matplotlib_font('FC Vision')

# ── Load data ─────────────────────────────────────────────────────────────────
df = pd.read_csv(ROOT / "output" / "data" / "hhi_tsic4.csv", dtype={"tsic4": str})
df = df.dropna(subset=["tsic_category", "hhi", "total_revenue"])
df = df[df["total_revenue"] > 0]

print(f"Plotting {len(df)} industries across {df['tsic_category'].nunique()} categories.")

# ── Color palette ─────────────────────────────────────────────────────────────
categories = sorted(df["tsic_category"].unique())
PALETTE = [
    "#2E4057", "#048A81", "#54C6EB", "#EF8D32", "#8EE3EF",
    "#B5EAD7", "#E63946", "#6D6875", "#C77DFF", "#F4A261",
    "#2A9D8F", "#E9C46A", "#264653", "#A8DADC", "#457B9D",
    "#F1FAEE", "#6A0572", "#D62828",
]
color_map = {cat: PALETTE[i % len(PALETTE)] for i, cat in enumerate(categories)}

DOT_SIZE = 80

# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 9), dpi=150)
fig.patch.set_facecolor("#F8F9FA")
ax.set_facecolor("#FFFFFF")

# ── Plot ──────────────────────────────────────────────────────────────────────
for cat in categories:
    subset = df[df["tsic_category"] == cat]
    ax.scatter(
        subset["total_revenue"],
        subset["hhi"],
        s=DOT_SIZE,
        c=color_map[cat],
        alpha=0.75,
        edgecolors="white",
        linewidths=0.6,
        zorder=3,
        label=cat,
    )

# ── Natural monopoly callouts ─────────────────────────────────────────────────
nm_df = df[df["natural_monopoly"] == "Natural Monopoly"]
for _, row in nm_df.iterrows():
    short = row["desc_en"][:30] + ("…" if len(row["desc_en"]) > 30 else "")
    ax.annotate(
        f"{row['tsic4']}\n{short}",
        xy=(row["total_revenue"], row["hhi"]),
        xytext=(12, 6),
        textcoords="offset points",
        fontsize=6.5,
        color="#2c3e50",
        arrowprops=dict(arrowstyle="-", color="#aaaaaa", lw=0.7),
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#cccccc", alpha=0.85),
        zorder=5,
    )

# ── HHI reference lines ───────────────────────────────────────────────────────
xlim_right = df["total_revenue"].max() * 2
for hhi_val, label, ls in [
    (2500, "Highly Concentrated (HHI >= 2,500)", "--"),
    (1500, "Moderately Concentrated (HHI >= 1,500)", ":"),
]:
    ax.axhline(hhi_val, color="#888888", linestyle=ls, linewidth=0.9, alpha=0.7, zorder=2)
    ax.text(
        xlim_right, hhi_val + 80,
        label,
        fontsize=7.5, color="#666666", ha="right", va="bottom",
    )

# ── X-axis: revenue formatted in THB ─────────────────────────────────────────
ax.set_xscale("log")

def fmt_thb(x, _):
    if x >= 1e12:
        return f"{x/1e12:.0f}T"
    elif x >= 1e9:
        return f"{x/1e9:.0f}B"
    elif x >= 1e6:
        return f"{x/1e6:.0f}M"
    return f"{x:.0f}"

from matplotlib.ticker import FuncFormatter
ax.xaxis.set_major_formatter(FuncFormatter(fmt_thb))

ax.set_xlabel("Total Industry Revenue — THB (log scale)", fontsize=12, labelpad=10, color="#333333")
ax.set_ylabel("Herfindahl-Hirschman Index (HHI)", fontsize=12, labelpad=10, color="#333333")
ax.set_title(
    "Market Concentration vs. Industry Revenue (TSIC 4-digit, FY2566)\n"
    "Color = ISIC Section",
    fontsize=14, fontweight="bold", pad=18, color="#1a1a2e"
)

ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.4, color="#AAAAAA")
ax.tick_params(axis="both", labelsize=10, colors="#444444")
ax.spines[["top", "right"]].set_visible(False)
ax.spines[["left", "bottom"]].set_color("#CCCCCC")

# ── Category legend ───────────────────────────────────────────────────────────
cat_desc = df.groupby("tsic_category")["tsic_category_desc"].first().to_dict()
legend_patches = [
    mpatches.Patch(
        color=color_map[cat],
        label=f"{cat}: {cat_desc.get(cat,'')[:35]}{'…' if len(cat_desc.get(cat,'')) > 35 else ''}"
    )
    for cat in categories
]
leg = ax.legend(
    handles=legend_patches,
    title="ISIC Section",
    loc="upper left",
    fontsize=7.5,
    title_fontsize=9,
    framealpha=0.92,
    edgecolor="#CCCCCC",
    ncol=2,
)
leg.get_title().set_fontweight("bold")
ax.add_artist(leg)

# ── Watermark ─────────────────────────────────────────────────────────────────
fig.text(
    0.98, 0.01,
    "Source: DBD Financial Statements FY2566  |  NESDC Analysis",
    ha="right", va="bottom", fontsize=7.5, color="#AAAAAA", style="italic"
)

# ── Save ──────────────────────────────────────────────────────────────────────
out_path = ROOT / "output" / "chart" / "hhi_scatter_revenue.png"
plt.tight_layout()
plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"Saved --> {out_path}")

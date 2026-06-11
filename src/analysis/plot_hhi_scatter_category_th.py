"""
plot_hhi_scatter_category_th.py
---------------------------------
@viz_expert — Thai-localized static bubble scatter (matplotlib):
  Y-axis  : Herfindahl-Hirschman Index (HHI)  [English, unchanged]
  X-axis  : จำนวนบริษัทที่ดำเนินการอยู่ (log scale)  [Thai]
  Bubble  : Total revenue — cube-root scaled
  Color   : TSIC Category section (A–S)
  Font    : FC Vision

Output : output/chart/hhi_scatter_category_th.png
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

# ── Font: FC Vision ───────────────────────────────────────────────────────────
FONTS_DIR = ROOT / "assets" / "fonts"
if FONTS_DIR.exists():
    for f in FONTS_DIR.rglob("*.ttf"):
        try:
            font_manager.fontManager.addfont(str(f))
        except Exception:
            pass
    for f in FONTS_DIR.rglob("*.otf"):
        try:
            font_manager.fontManager.addfont(str(f))
        except Exception:
            pass

FONT_FAMILY = "FC Vision"
plt.rcParams["font.family"] = FONT_FAMILY
plt.rcParams["axes.unicode_minus"] = False

# ── Load data ─────────────────────────────────────────────────────────────────
df = pd.read_csv(ROOT / "output" / "data" / "hhi_tsic4.csv", dtype={"tsic4": str})
df = df.dropna(subset=["tsic_category", "hhi", "active_firms", "total_revenue"])
df = df[df["active_firms"] > 0]
df = df[df["total_revenue"] > 0]

print(f"Plotting {len(df)} industries across {df['tsic_category'].nunique()} categories.")

def load_tsic_category_th():
    candidates = list((ROOT / "input").rglob("TSIC_descriptions.xlsx"))
    candidates.append(ROOT / "output" / "data" / "TSIC_descriptions.xlsx")

    category_df = None
    for tsic_path in candidates:
        if not tsic_path.exists():
            continue
        try:
            category_df = pd.read_excel(tsic_path, sheet_name="หมวดใหญ่")
            break
        except PermissionError:
            continue

    if category_df is None:
        print("TSIC dictionary not readable; using category descriptions from hhi_tsic4.csv.")
        return {}

    category_df["หมวดใหญ่"] = category_df["หมวดใหญ่"].astype(str).str.strip()
    return dict(zip(category_df["หมวดใหญ่"], category_df["คำอธิบาย"]))

# ── Bubble size: cube-root scaling ────────────────────────────────────────────
cbrt_rev  = df["total_revenue"] ** (1 / 3)
min_cr    = cbrt_rev.min()
max_cr    = cbrt_rev.max()
# Scale to [25, 1800] for matplotlib scatter s parameter (area)
bubble_sizes = 25 + ((cbrt_rev - min_cr) / (max_cr - min_cr)) * 1775

# ── Perceptually distinct palette (same as Plotly version) ───────────────────
PALETTE = {
    "A": "#E6194B",
    "B": "#3CB44B",
    "C": "#4363D8",
    "D": "#F58231",
    "E": "#42D4F4",
    "F": "#F032E6",
    "G": "#BFEF45",
    "H": "#FABED4",
    "I": "#469990",
    "J": "#DCBEFF",
    "K": "#9A6324",
    "L": "#FFFAC8",
    "M": "#800000",
    "N": "#AAFFC3",
    "O": "#808000",
    "P": "#FFD8B1",
    "Q": "#000075",
    "R": "#A9A9A9",
    "S": "#FF4500",
}

categories = sorted(df["tsic_category"].unique())
cat_desc_en = df.groupby("tsic_category")["tsic_category_desc"].first().to_dict()
cat_desc_th = load_tsic_category_th()
cat_desc = {cat: cat_desc_th.get(cat, cat_desc_en.get(cat, "")) for cat in categories}

# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(22, 11), dpi=160)
fig.patch.set_facecolor("#F8F9FA")
ax.set_facecolor("#FFFFFF")

# ── Plot ──────────────────────────────────────────────────────────────────────
for cat in categories:
    subset = df[df["tsic_category"] == cat]
    ax.scatter(
        subset["active_firms"],
        subset["hhi"],
        s=bubble_sizes[subset.index],
        c=PALETTE.get(cat, "#888888"),
        alpha=0.75,
        edgecolors="white",
        linewidths=0.6,
        zorder=3,
        label=cat,
    )

# ── Vertical reference line at 100 firms ─────────────────────────────────────
ax.axvline(100, color="#888888", linestyle="--", linewidth=1.3, alpha=0.85, zorder=2)
vline_label = ax.text(
    103, ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else df["hhi"].max() * 0.98,
    "100 บริษัท",
    fontsize=13, color="#666666", va="top", ha="left",
)

# ── Horizontal concentration standard lines ──────────────────────────────────
for y_value, label, y_offset, va in [
    (1800, "US FTC Standard", -6, "top"),
    (2000, "EU Commission Standard", 6, "bottom"),
]:
    ax.axhline(
        y_value,
        color="#C0392B",
        linestyle="--",
        linewidth=1.6,
        alpha=0.9,
        zorder=2,
    )
    ax.annotate(
        label,
        xy=(0.995, y_value),
        xycoords=ax.get_yaxis_transform(),
        xytext=(0, y_offset),
        textcoords="offset points",
        fontsize=13,
        color="#C0392B",
        va=va,
        ha="right",
        backgroundcolor=(1, 1, 1, 0.72),
    )

# ── Axes ──────────────────────────────────────────────────────────────────────
ax.set_xscale("log")
ax.set_xlabel("จำนวนบริษัทที่ดำเนินการอยู่ (log scale)", fontsize=19, labelpad=16, color="#333333")
ax.set_ylabel("Herfindahl-Hirschman Index (HHI)", fontsize=19, labelpad=16, color="#333333")

ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.4, color="#AAAAAA")
ax.tick_params(axis="both", labelsize=14, colors="#444444")
ax.spines[["top", "right"]].set_visible(False)
ax.spines[["left", "bottom"]].set_color("#CCCCCC")

# ── Legend: categories ────────────────────────────────────────────────────────
legend_patches = []
for cat in categories:
    desc  = cat_desc.get(cat, "")
    legend_patches.append(
        mpatches.Patch(color=PALETTE.get(cat, "#888888"), label=f"{cat}: {desc}")
    )

leg = ax.legend(
    handles=legend_patches,
    title="กลุ่มการผลิต",
    loc="upper left",
    bbox_to_anchor=(1.015, 1.0),
    fontsize=11,
    title_fontsize=13,
    framealpha=0.92,
    edgecolor="#CCCCCC",
    ncol=1,
    borderpad=0.8,
    labelspacing=0.7,
    handlelength=1.8,
)
leg.get_title().set_fontweight("bold")

# ── Save ──────────────────────────────────────────────────────────────────────
out_path = ROOT / "output" / "chart" / "hhi_scatter_category_th.png"
fig.subplots_adjust(left=0.07, right=0.66, top=0.96, bottom=0.12)

# Re-draw the vline annotation after tight_layout adjusts limits
vline_label.remove()
ymax = ax.get_ylim()[1]
ax.text(103, ymax * 0.97, "100 บริษัท", fontsize=13, color="#666666", va="top", ha="left")

plt.savefig(out_path, dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"Saved --> {out_path}")

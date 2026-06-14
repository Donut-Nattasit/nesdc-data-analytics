"""
plot_hhi_scatter_category.py
----------------------------
Interactive bubble scatter chart (Plotly):
  Y-axis  : HHI (Herfindahl-Hirschman Index)
  X-axis  : Number of active firms (log scale)
  Bubble  : Total revenue, cube-root scaled
  Color   : TSIC Category section (A-S)
  Hover   : TSIC4, Industry name, HHI, CR1, CR4, CR8, Active Firms, Revenue,
            Natural Monopoly label

Outputs:
  output/chart/hhi_scatter_category.html
  output/chart/hhi_scatter_category.png, when static export support is available
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

df = pd.read_csv(ROOT / "output" / "data" / "hhi_tsic4.csv", dtype={"tsic4": str})
df = df.dropna(subset=["tsic_category", "hhi", "active_firms", "total_revenue"])
df = df[df["active_firms"] > 0]
df = df[df["total_revenue"] > 0]

print(f"Plotting {len(df)} industries across {df['tsic_category'].nunique()} categories.")

# Bubble size: cube-root scaling gives visible variation while keeping the
# largest revenue sectors from overwhelming the plot.
cbrt_rev = np.cbrt(df["total_revenue"])
min_cr = cbrt_rev.min()
max_cr = cbrt_rev.max()
if max_cr == min_cr:
    df["bubble_size"] = 28
else:
    df["bubble_size"] = 8 + ((cbrt_rev - min_cr) / (max_cr - min_cr)) * 72

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


def fmt_thb(val):
    if val >= 1e12:
        return f"{val / 1e12:.2f}T THB"
    if val >= 1e9:
        return f"{val / 1e9:.2f}B THB"
    if val >= 1e6:
        return f"{val / 1e6:.2f}M THB"
    return f"{val:,.0f} THB"


df["hover"] = df.apply(
    lambda r: (
        f"<b>[{r['tsic4']}] {r['desc_en']}</b><br>"
        f"<b>Category:</b> {r['tsic_category']} - {r['tsic_category_desc']}<br>"
        f"<b>HHI:</b> {r['hhi']:,.1f}<br>"
        f"<b>CR1:</b> {r['cr1'] * 100:.1f}%  |  "
        f"<b>CR4:</b> {r['cr4'] * 100:.1f}%  |  "
        f"<b>CR8:</b> {r['cr8'] * 100:.1f}%<br>"
        f"<b>Active Firms:</b> {int(r['active_firms']):,}<br>"
        f"<b>Total Revenue:</b> {fmt_thb(r['total_revenue'])}<br>"
        f"<b>Natural Monopoly:</b> {r['natural_monopoly']}"
    ),
    axis=1,
)

fig = go.Figure()

categories = sorted(df["tsic_category"].unique())
cat_desc = df.groupby("tsic_category")["tsic_category_desc"].first().to_dict()

for cat in categories:
    sub = df[df["tsic_category"] == cat]
    color = PALETTE.get(cat, "#888888")
    desc_short = cat_desc.get(cat, "")
    if len(desc_short) > 40:
        desc_short = desc_short[:40] + "..."
    label = f"{cat}: {desc_short}"

    fig.add_trace(
        go.Scatter(
            x=sub["active_firms"],
            y=sub["hhi"],
            mode="markers",
            name=label,
            marker=dict(
                size=sub["bubble_size"],
                sizemode="diameter",
                color=color,
                opacity=0.78,
                line=dict(width=0.8, color="white"),
            ),
            hovertemplate=sub["hover"] + "<extra></extra>",
            customdata=sub[["tsic4", "desc_en", "natural_monopoly"]].values,
        )
    )

fig.add_vline(
    x=100,
    line_dash="dash",
    line_color="#888888",
    line_width=1.4,
    annotation_text="100 firms",
    annotation_position="top right",
    annotation_font=dict(size=11, color="#888888"),
)

nm_df = df[df["natural_monopoly"] == "Natural Monopoly"]
for _, row in nm_df.iterrows():
    fig.add_annotation(
        x=row["active_firms"],
        y=row["hhi"],
        xref="x",
        yref="y",
        text=f"<b>{row['tsic4']}</b>",
        showarrow=False,
        font=dict(size=9, color="#333333"),
        bgcolor="rgba(255,255,255,0.75)",
        bordercolor="#cccccc",
        borderwidth=1,
        xanchor="left",
        yanchor="bottom",
        xshift=8,
        yshift=4,
    )

fig.update_layout(
    title=dict(
        text=(
            "<b>Market Concentration by Industry (TSIC 4-digit, FY2566)</b><br>"
            "<sup>Bubble size = Total Revenue (cube-root scale) | Color = ISIC Section</sup>"
        ),
        x=0.5,
        xanchor="center",
        font=dict(size=18, family="FC Vision, Arial, sans-serif", color="#1a1a2e"),
    ),
    xaxis=dict(
        title=dict(
            text="Number of Active Firms (log scale)",
            font=dict(size=13, family="FC Vision, Arial, sans-serif"),
        ),
        type="log",
        tickfont=dict(size=11, family="FC Vision, Arial, sans-serif"),
        gridcolor="#E9ECEF",
        gridwidth=0.5,
        showline=True,
        linecolor="#CCCCCC",
    ),
    yaxis=dict(
        title=dict(
            text="Herfindahl-Hirschman Index (HHI)",
            font=dict(size=13, family="FC Vision, Arial, sans-serif"),
        ),
        tickfont=dict(size=11, family="FC Vision, Arial, sans-serif"),
        gridcolor="#E9ECEF",
        gridwidth=0.5,
        showline=True,
        linecolor="#CCCCCC",
    ),
    legend=dict(
        title=dict(text="ISIC Section", font=dict(size=12, family="FC Vision, Arial, sans-serif")),
        font=dict(size=10, family="FC Vision, Arial, sans-serif"),
        bgcolor="rgba(255,255,255,0.92)",
        bordercolor="#DDDDDD",
        borderwidth=1,
        orientation="v",
        x=1.01,
        y=1,
        xanchor="left",
    ),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#F8F9FA",
    font=dict(family="FC Vision, Arial, sans-serif"),
    hoverlabel=dict(
        bgcolor="white",
        font_size=12,
        font_family="FC Vision, Arial, sans-serif",
        bordercolor="#DDDDDD",
    ),
    margin=dict(l=70, r=250, t=100, b=80),
    annotations=[
        *fig.layout.annotations,
        dict(
            text="Source: DBD Financial Statements FY2566 | NESDC Analysis",
            xref="paper",
            yref="paper",
            x=1.0,
            y=-0.07,
            showarrow=False,
            font=dict(size=10, color="#AAAAAA", style="italic"),
            xanchor="right",
        ),
    ],
    width=1300,
    height=800,
)

for rev_val, label in [(1e9, "1B THB"), (1e11, "100B THB"), (1e12, "1T THB")]:
    cr = rev_val ** (1 / 3)
    if max_cr == min_cr:
        size = 28
    else:
        size = 8 + ((cr - min_cr) / (max_cr - min_cr)) * 72
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(
                size=size,
                sizemode="diameter",
                color="#BBBBBB",
                opacity=0.6,
                line=dict(width=1, color="white"),
            ),
            name=label,
            showlegend=True,
            legendgroup="revenue",
            legendgrouptitle=dict(text="Total Revenue"),
            hoverinfo="skip",
        )
    )

html_path = ROOT / "output" / "chart" / "hhi_scatter_category.html"
fig.write_html(
    str(html_path),
    include_plotlyjs=True,
    full_html=True,
    config={"scrollZoom": True, "displayModeBar": True, "responsive": True},
)
print(f"Saved HTML --> {html_path}")

png_path = ROOT / "output" / "chart" / "hhi_scatter_category.png"
try:
    fig.write_image(str(png_path), scale=1.5)
    print(f"Saved PNG  --> {png_path}")
except Exception as exc:
    print(f"PNG export skipped (kaleido not available): {exc}")
    print("Open the HTML file for the full interactive version.")

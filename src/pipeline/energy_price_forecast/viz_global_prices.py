import os
import sys
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# Enforce UTF-8 encoding for standard console output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.visualization.charts import configure_matplotlib_font, save_chart
from src.utils.registry import add_visualization

def main():
    print("==========================================================")
    print("[Global Prices Viz] Generating Global Benchmarks Chart...")
    print("==========================================================")
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    data_path = project_root / "output" / "data" / "energy_price_forecast" / "dubai_oil_forecast_production.csv"
    
    if not data_path.exists():
        print(f"[Error] Forecast dataset not found at: {data_path}")
        raise RuntimeError("Pipeline step failed")
        
    # Load Forecast CSV
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Filter full projection period (Jan 2024 - Dec 2027)
    df_filtered = df[(df['date'] >= '2024-01-01') & (df['date'] <= '2027-12-01')].copy()
    df_filtered = df_filtered.sort_values(by='date').reset_index(drop=True)
    
    if df_filtered.empty:
        print("[Error] No data found in specified range. Exiting.")
        raise RuntimeError("Pipeline step failed")
        
    # Dynamically find forecast origin
    forecast_origin = df_filtered[df_filtered['dubai_spot'].notna()]['date'].max()
    print(f"  Forecast Origin (Last Actual Month): {forecast_origin.strftime('%Y-%m-%d')}")
    
    df_hist = df_filtered[df_filtered['date'] <= forecast_origin].copy()
    df_fc = df_filtered[df_filtered['date'] >= forecast_origin].copy()
    
    print(f"Loaded {len(df_hist)} historical and {len(df_fc)} forecast observations.")
    
    # Render Chart
    configure_matplotlib_font(font_name='FC Vision')
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    
    # 1. Plotting the lines (solid for actuals, dashed for forecasts)
    # Dubai Fateh: Sapphire Blue (Primary target focus)
    ax.plot(
        df_hist['date'], df_hist['dubai_spot'],
        color='#00109E', linestyle='-', linewidth=2.5,
        marker='o', markersize=5.5, label='Dubai Spot (Historical / Forecast)'
    )
    ax.plot(
        df_fc['date'], df_fc['dubai_spot_forecast'],
        color='#00109E', linestyle='--', linewidth=2.0,
        marker='o', markersize=4.5, label='_nolegend_'
    )
    
    # Brent Spot: Support Teal-Cyan
    ax.plot(
        df_hist['date'], df_hist['brent_spot'],
        color='#14b8a6', linestyle='-', linewidth=2.0,
        marker='s', markersize=5.0, label='Brent Spot (Historical / Forecast)'
    )
    ax.plot(
        df_fc['date'], df_fc['brent_spot'],
        color='#14b8a6', linestyle='--', linewidth=1.5,
        marker='s', markersize=4.0, label='_nolegend_'
    )
    
    # WTI Spot: Neutral Clay
    ax.plot(
        df_hist['date'], df_hist['wti_spot'],
        color='#bfb997', linestyle='-', linewidth=2.0,
        marker='^', markersize=5.0, label='WTI Spot (Historical / Forecast)'
    )
    ax.plot(
        df_fc['date'], df_fc['wti_spot'],
        color='#bfb997', linestyle='--', linewidth=1.5,
        marker='^', markersize=4.0, label='_nolegend_'
    )
    
    # 2. Add Key Event Annotations / Marks
    # Event A: June 2024 - OPEC+ cuts extension
    opec_date = pd.Timestamp("2024-06-01")
    opec_y = df_hist[df_hist['date'] == opec_date]['dubai_spot'].values[0]
    ax.annotate(
        "OPEC+ JMMC Extends\nVoluntary Cuts (2.2 mb/d)",
        xy=(opec_date, opec_y),
        xytext=(opec_date - pd.DateOffset(days=50), opec_y - 12),
        arrowprops=dict(facecolor='#64748b', shrink=0.08, width=0.8, headwidth=5, edgecolor='none'),
        color='#475569', fontweight='medium', fontsize=8.5, ha='center',
        bbox=dict(boxstyle="round,pad=0.2", fc="#ffffff", ec="#e2e8f0", lw=0.5, alpha=0.85)
    )
    
    # Event B: January 2025 - Red Sea shipping diversion escalates freight rates
    redsea_date = pd.Timestamp("2025-01-01")
    redsea_y = df_hist[df_hist['date'] == redsea_date]['brent_spot'].values[0]
    ax.annotate(
        "Red Sea Shipping Diversions\nEscalate Freight Rates",
        xy=(redsea_date, redsea_y),
        xytext=(redsea_date - pd.DateOffset(days=40), redsea_y + 10),
        arrowprops=dict(facecolor='#64748b', shrink=0.08, width=0.8, headwidth=5, edgecolor='none'),
        color='#475569', fontweight='medium', fontsize=8.5, ha='center',
        bbox=dict(boxstyle="round,pad=0.2", fc="#ffffff", ec="#e2e8f0", lw=0.5, alpha=0.85)
    )
    
    # Event C: March 2026 - Strait of Hormuz shipping disruptions peak
    hormuz_date = pd.Timestamp("2026-03-01")
    hormuz_y = df_hist[df_hist['date'] == hormuz_date]['dubai_spot'].values[0]
    ax.annotate(
        "Strait of Hormuz physical transit\ndisruptions peak (Dubai peaks at $128.8)",
        xy=(hormuz_date, hormuz_y),
        xytext=(hormuz_date - pd.DateOffset(days=120), hormuz_y + 12),
        arrowprops=dict(facecolor='#00109E', shrink=0.08, width=1.0, headwidth=6, edgecolor='none'),
        color='#00109E', fontweight='bold', fontsize=9.0, ha='center',
        bbox=dict(boxstyle="round,pad=0.3", fc="#f8fafc", ec="#00109E", lw=1.0, alpha=0.9)
    )
    
    # Event D: May 2026 - OPEC+ meeting on voluntary adjustments
    may_date = pd.Timestamp("2026-05-01")
    may_y = df_hist[df_hist['date'] == may_date]['dubai_spot'].values[0]
    ax.annotate(
        "OPEC+ Agrees to\n188k b/d Adj.",
        xy=(may_date, may_y),
        xytext=(may_date + pd.DateOffset(days=50), may_y - 12),
        arrowprops=dict(facecolor='#14b8a6', shrink=0.08, width=0.8, headwidth=5, edgecolor='none'),
        color='#0f766e', fontweight='medium', fontsize=8.5, ha='center',
        bbox=dict(boxstyle="round,pad=0.2", fc="#ffffff", ec="#e2e8f0", lw=0.5, alpha=0.85)
    )
    
    # Vertical line at forecast origin
    ax.axvline(x=forecast_origin, color='#94a3b8', linestyle=':', linewidth=1.5)
    
    # Shade the forecast region to highlight outlook bounds
    ax.axvspan(forecast_origin, df_filtered['date'].max(), color='#f8fafc', alpha=0.6)
    ax.text(
        forecast_origin + pd.DateOffset(days=20), 140,
        f'Forecast Region\n(starts {forecast_origin.strftime("%b %Y")})',
        color='#475569', fontsize=9, fontweight='bold', ha='left'
    )
    
    # Titles and formatting (Using centered isolated titles per viz_expert rules)
    fig.suptitle("Global Crude Oil Price Benchmarks & Projections (2024 - 2027)", fontsize=16, fontweight='bold', x=0.5, y=0.97, ha='center')
    ax.set_title("Historical monthly spot actuals and forecast price paths to December 2027", fontsize=10, color='#64748b', pad=10, loc='center')
    
    # Axes limits and labels
    ax.set_ylabel("Price (USD / Barrel)", fontsize=11, fontweight='bold', labelpad=10)
    ax.set_xlabel(None)
    ax.xaxis.label.set_visible(False)
    ax.set_ylim(45, 150)
    
    # Customize grid and spines
    ax.grid(True, which='both', linestyle='-', color='#e2e8f0', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    
    # Legend
    ax.legend(loc='lower left', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', framealpha=0.9, fontsize=9.5)
    
    # Date formatting
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
    plt.xticks(rotation=30, ha='right')
    
    # Add source attribution
    fig.text(0.08, 0.02, "Source: Bloomberg (GIOS0097), U.S. EIA Short-Term Energy Outlook database", fontsize=8.5, color='#64748b', ha='left', family='FC Vision')
    
    plt.tight_layout()
    fig.subplots_adjust(top=0.88, bottom=0.18)
    
    # Save figure
    out_chart_path = "output/chart/energy_price_forecast/dubai_oil_global_oil_prices_comparison.png"
    # Ensure subdirectory exists
    Path(out_chart_path).parent.mkdir(parents=True, exist_ok=True)
    save_chart(fig, out_chart_path, save_html=False)
    print(f"✅ Successfully generated and saved global prices chart to: {out_chart_path}")
    
    # Register visualization
    try:
        add_visualization(
            name="Global Crude Price Comparison",
            chart_type="Multi-Series Line with Annotations",
            source_data="output/data/energy_price_forecast/dubai_oil_forecast_production.csv",
            png_path=out_chart_path,
            status="Rendered"
        )
        print("✅ Registered new visualization in registry.")
    except Exception as e:
        print(f"⚠️ Failed to register visualization: {e}")

if __name__ == "__main__":
    main()

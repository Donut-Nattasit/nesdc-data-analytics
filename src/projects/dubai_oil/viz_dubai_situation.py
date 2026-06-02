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

def main():
    print("==========================================================")
    print("[Dubai Situation Viz] Generating Dubai Crude Situation Chart...")
    print("==========================================================")
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    current_yyyy_mm = datetime.now().strftime("%Y-%m")
    excel_path = project_root / "input" / "projects" / "dubai_oil" / "dubai_price.xlsx"
    
    if not excel_path.exists():
        print(f"[Error] Excel file not found at: {excel_path}")
        sys.exit(1)
        
    # Load Spot Sheet
    print("Loading daily spot price data...")
    df_raw = pd.read_excel(excel_path, sheet_name="spot")
    df_raw['date'] = pd.to_datetime(df_raw['date'])
    
    # Filter 2026 actuals (ignore forecast parts)
    df_2026 = df_raw[df_raw['date'] >= '2026-01-01'].copy()
    df_2026 = df_2026.dropna(subset=['GIOS0097 Index']).sort_values('date').reset_index(drop=True)
    
    if df_2026.empty:
        print("[Error] No spot data found for 2026. Exiting.")
        sys.exit(1)
        
    print(f"Loaded {len(df_2026)} actual trading days from {df_2026['date'].min().strftime('%Y-%m-%d')} to {df_2026['date'].max().strftime('%Y-%m-%d')}.")
    
    # 1. Compute Expanding YTD Cumulative Average
    # For each trading day, expanding mean computes the average from the start of 2026 up to that day.
    df_2026['ytd_avg'] = df_2026['GIOS0097 Index'].expanding().mean()
    
    # 2. Compute Monthly Averages
    df_2026['month'] = df_2026['date'].dt.to_period('M')
    df_monthly = df_2026.groupby('month').agg(
        monthly_avg=('GIOS0097 Index', 'mean'),
        date_pos=('date', 'max') # Plot monthly averages at the end of the month
    ).reset_index()
    
    # Compute MoM and YoY changes dynamically using all historical daily actuals
    df_all_spot = df_raw.dropna(subset=['GIOS0097 Index']).sort_values('date').copy()
    df_all_monthly = df_all_spot.resample('MS', on='date')['GIOS0097 Index'].mean().reset_index()
    df_all_monthly['month'] = df_all_monthly['date'].dt.to_period('M')
    df_all_monthly['mom_pct'] = df_all_monthly['GIOS0097 Index'].pct_change(1) * 100
    df_all_monthly['yoy_pct'] = df_all_monthly['GIOS0097 Index'].pct_change(12) * 100
    
    # Merge MoM and YoY calculations back into df_monthly
    df_monthly = pd.merge(df_monthly, df_all_monthly[['month', 'mom_pct', 'yoy_pct']], on='month', how='left')
    
    print("\nCalculated Monthly Averages (Dynamic MoM & YoY):")
    for idx, row in df_monthly.iterrows():
        mom_str = f"{row['mom_pct']:+.1f}%" if pd.notnull(row['mom_pct']) else "N/A"
        yoy_str = f"{row['yoy_pct']:+.1f}%" if pd.notnull(row['yoy_pct']) else "N/A"
        print(f"  - {row['month']}: Avg = ${row['monthly_avg']:.2f}, MoM = {mom_str}, YoY = {yoy_str}, Last Trading Day = {row['date_pos'].strftime('%Y-%m-%d')}")
        
    latest_ytd = df_2026['ytd_avg'].iloc[-1]
    latest_date = df_2026['date'].iloc[-1]
    print(f"\nLatest Cumulative YTD Average (as of {latest_date.strftime('%Y-%m-%d')}): ${latest_ytd:.2f}/bbl")
    
    # Save the prepared table to a CSV for report integration or quick reference
    tbl_path = project_root / "output" / "report" / "price_forecast" / current_yyyy_mm / "data" / "transformed" / "dubai_situation_2026.csv"
    df_monthly_out = df_monthly.copy()
    # Compute cumulative YTD at the end of each month
    monthly_ytd = []
    for dt in df_monthly['date_pos']:
        ytd_val = df_2026[df_2026['date'] <= dt]['GIOS0097 Index'].mean()
        monthly_ytd.append(ytd_val)
    df_monthly_out['ytd_avg'] = monthly_ytd
    df_monthly_out.to_csv(tbl_path, index=False)
    print(f"Saved situation data table to: {tbl_path}")
    
    # 3. Render Chart
    configure_matplotlib_font(font_name='FC Vision')
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    
    # Plot Daily actuals (grey line, alpha 0.5)
    ax.plot(
        df_2026['date'], df_2026['GIOS0097 Index'],
        color='#cbd5e1', linestyle='-', linewidth=1.2, alpha=0.7,
        label='Daily Dubai Spot (GIOS0097 Index)'
    )
    
    # Plot Cumulative YTD (brand support teal line)
    ax.plot(
        df_2026['date'], df_2026['ytd_avg'],
        color='#0d9488', linestyle='-', linewidth=2.5,
        label='Year-to-Date (YTD) Cumulative Average'
    )
    
    # Plot Monthly Averages (official Sapphire Blue line with markers)
    ax.plot(
        df_monthly['date_pos'], df_monthly['monthly_avg'],
        color='#00109E', linestyle='--', linewidth=2.0,
        marker='o', markersize=8, markeredgecolor='#00109E', markerfacecolor='#60B1E7',
        label='Monthly Average Spot Price'
    )
    
    # Dynamic offsets and white background boxes for monthly points to prevent overlaps
    offsets = [
        (-12, 4, 'right'),  # Jan: left of the point
        (-12, 4, 'right'),  # Feb: left of the point
        (0, 12, 'center'),  # Mar: above the point
        (0, 12, 'center'),  # Apr: above the point
        (12, 4, 'left'),    # May: right of the point
    ]
    for idx, row in df_monthly.iterrows():
        if idx < len(offsets):
            offset_x, offset_y, align = offsets[idx]
        else:
            offset_x, offset_y, align = (12, 4, 'left') # Fallback for future months
            
        ax.annotate(
            f"${row['monthly_avg']:.1f}",
            xy=(row['date_pos'], row['monthly_avg']),
            xytext=(offset_x, offset_y), textcoords='offset points',
            ha=align, fontweight='bold', color='#00109E', fontsize=9.5,
            bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#cbd5e1", lw=0.5, alpha=0.85)
        )
        
    # Annotate latest YTD
    ax.annotate(
        f"Latest YTD Average\n(As of {latest_date.strftime('%b %d, %Y')}): ${latest_ytd:.2f}",
        xy=(latest_date, latest_ytd),
        xytext=(latest_date - pd.DateOffset(days=22), latest_ytd - 13),
        arrowprops=dict(facecolor='#0d9488', shrink=0.08, width=1, headwidth=6, edgecolor='none'),
        color='#0f766e', fontweight='bold', fontsize=10,
        bbox=dict(boxstyle="round,pad=0.3", fc="#f0fdfa", ec="#0d9488", lw=1, alpha=0.9)
    )
    
    # Titles and formatting (Using centered isolated titles per viz_expert rules)
    fig.suptitle("Dubai Crude Oil Price in 2026", fontsize=16, fontweight='bold', x=0.5, y=0.97, ha='center')
    ax.set_title("Physical Spot Actuals, Resampled Monthly Averages & Expanding YTD Cumulative Average", fontsize=10, color='#64748b', pad=10, loc='center')
    
    # Generic axis label suppressed, concrete metric retained on Y axis
    ax.set_ylabel("Price (USD / Barrel)", fontsize=11, fontweight='bold', labelpad=10)
    ax.set_xlabel(None)
    ax.xaxis.label.set_visible(False)
    
    ax.grid(True, which='both', linestyle='-', color='#e2e8f0', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    
    # Legend placed in upper left (completely clears lower-left noise)
    ax.legend(loc='upper left', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', framealpha=0.9, fontsize=10)
    
    # Date formatting with rotation
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=30, ha='right')
    
    # Add source attribution
    fig.text(0.08, 0.02, "Source: Bloomberg (GIOS0097 Index daily actual spot prices)", fontsize=8.5, color='#64748b', ha='left', family='FC Vision')
    
    # Adjust tight layout and bottom margin for clean spacing
    plt.tight_layout()
    fig.subplots_adjust(top=0.88, bottom=0.18)
    
    # Save figure
    out_chart_path = f"output/report/price_forecast/{current_yyyy_mm}/chart/dubai_oil_situation.png"
    save_chart(fig, out_chart_path, save_html=False)
    print(f"✅ Successfully generated and saved situation line chart to: {out_chart_path}")

if __name__ == "__main__":
    main()

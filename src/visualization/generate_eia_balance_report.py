import os
import sys
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

# Add project root to system path to import clients
sys.path.append('.')
from src.api.eia_client import EIAClient
from src.visualization.charts import configure_matplotlib_font, save_chart

def build_charts(df, thai_locale=False):
    """
    Renders the dual-subplot World Petroleum Balance chart.
    Top: Supply and Demand line chart.
    Bottom: Stock Changes vertical bar chart.
    """
    # 1. Configure typography and theme
    font_name = 'FC Vision'
    configure_matplotlib_font(font_name)
    
    # 2. Setup figure with shared X axis and custom height ratio (2:1)
    fig, (ax1, ax2) = plt.subplots(
        2, 1, 
        sharex=True, 
        figsize=(11, 8), 
        gridspec_kw={'height_ratios': [2.2, 1]}
    )
    
    # Define labels based on locale
    if thai_locale:
        # Title Strings
        fig_title = "สมดุลปิโตรเลียมโลก (EIA Short-Term Energy Outlook)"
        top_title = "อุปสงค์ปิโตรเลียมโลกและการผลิต (Demand vs. Supply)"
        bottom_title = "การเปลี่ยนแปลงปริมาณสำรองสุทธิ (Inventory Net Withdrawals)"
        
        # Series Names
        supply_label = "อุปทาน (กำลังการผลิต)"
        demand_label = "อุปสงค์ (ปริมาณการบริโภค)"
        bar_label = "การดึงน้ำมันออกสุทธิ (Net Draws)"
        build_label = "การสะสมในคลังสำรองสุทธิ (Net Builds)"
        
        # Unit Labels
        y_unit = "ล้านบาร์เรลต่อวัน (mb/d)"
    else:
        # Title Strings
        fig_title = "EIA Short-Term Energy Outlook: World Petroleum Balance"
        top_title = "World Petroleum Supply and Demand"
        bottom_title = "World Inventory Net Withdrawals (Stock Changes)"
        
        # Series Names
        supply_label = "World Production (Supply)"
        demand_label = "World Consumption (Demand)"
        bar_label = "Net Inventory Withdrawals (Draws)"
        build_label = "Net Inventory Accumulations (Builds)"
        
        # Unit Labels
        y_unit = "Million Barrels per Day (mb/d)"
        
    # --- Top Subplot: Supply & Demand Lines ---
    ax1.plot(
        df['date'], df['PAPR_WORLD'], 
        color='#1a365d', linewidth=2.5, 
        marker='o', markersize=4.5, 
        label=supply_label
    )
    ax1.plot(
        df['date'], df['PATC_WORLD'], 
        color='#e53e3e', linewidth=2.5, 
        marker='s', markersize=4.5, 
        label=demand_label
    )
    
    ax1.set_title(top_title, fontsize=13, fontweight='bold', pad=10, loc='left')
    ax1.set_ylabel(y_unit, fontsize=10, fontweight='medium')
    ax1.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='#e2e8f0', framealpha=0.9, fontsize=9.5)
    ax1.grid(True, linestyle=':', alpha=0.6, color='#cbd5e1')
    
    # --- Bottom Subplot: Stock Changes Bars ---
    # Custom color scheme: Teal/Green for draws (positive), Grey for builds (negative)
    colors = ['#2f855a' if val >= 0 else '#718096' for val in df['T3_STCHANGE_WORLD']]
    
    # Width of bars in days (~60 days is ideal for quarterly dates spaced by ~90 days)
    ax2.bar(
        df['date'], df['T3_STCHANGE_WORLD'], 
        width=60, color=colors, 
        edgecolor='none', alpha=0.9
    )
    
    # Draw reference line at zero
    ax2.axhline(0, color='#475569', linestyle='--', linewidth=0.8)
    
    ax2.set_title(bottom_title, fontsize=12, fontweight='bold', pad=10, loc='left')
    ax2.set_ylabel(y_unit, fontsize=10, fontweight='medium')
    
    # Add manual custom legend to explain bar colors
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2f855a', label=bar_label),
        Patch(facecolor='#718096', label=build_label)
    ]
    ax2.legend(handles=legend_elements, loc='upper left', frameon=True, facecolor='white', edgecolor='#e2e8f0', framealpha=0.9, fontsize=9)
    ax2.grid(True, linestyle=':', alpha=0.6, color='#cbd5e1')
    
    # --- X-Axis Formatting & Spacing Optimization ---
    # Show Q1 (Jan) and Q3 (Jul) of every year to keep the labels elegant and readable
    ax2.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    
    # Custom FuncFormatter for quarterly dates
    def quarterly_formatter(val, pos):
        d = mdates.num2date(val)
        quarter = (d.month - 1) // 3 + 1
        if thai_locale:
            year_be = d.year + 543
            return f"Q{quarter}-{year_be}"
        else:
            return f"Q{quarter} {d.year}"
            
    ax2.xaxis.set_major_formatter(FuncFormatter(quarterly_formatter))
    
    # Rotate bottom tick labels slightly for premium legibility
    plt.setp(ax2.get_xticklabels(), rotation=35, ha='right', fontsize=9.5, fontweight='medium')
    
    # Completely remove top subplot's visible tick text (retains alignment via sharex)
    plt.setp(ax1.get_xticklabels(), visible=False)
    
    # Remove all X-axis title labels to ensure a highly compact zero-blank-space layout
    ax1.xaxis.label.set_visible(False)
    ax2.xaxis.label.set_visible(False)
    
    # --- Main Figure Enhancements ---
    fig.suptitle(fig_title, fontsize=16, fontweight='bold', y=0.97)
    
    # Auto layout adjustment
    plt.tight_layout()
    # Pull top and bottom plots extremely close to each other
    plt.subplots_adjust(hspace=0.12, top=0.89, bottom=0.15)
    
    return fig

def main():
    # ---- CLI Argument Parsing (for skill invocations) ----
    parser = argparse.ArgumentParser(
        description='EIA STEO World Petroleum Balance Quarterly Chart Generator'
    )
    parser.add_argument(
        '--force-refresh', action='store_true', default=False,
        help='Force bypass of local cache and pull latest data from EIA API (use after new STEO release)'
    )
    parser.add_argument(
        '--start-date', type=str, default='2020-01-01',
        help='Start of display window in YYYY-MM-DD format (default: 2020-01-01)'
    )
    parser.add_argument(
        '--end-date', type=str, default='2027-12-31',
        help='End of display window in YYYY-MM-DD format (default: 2027-12-31)'
    )
    parser.add_argument(
        '--locale', type=str, choices=['both', 'eng', 'thai'], default='both',
        help='Which locale(s) to render: both (default), eng, or thai'
    )
    args = parser.parse_args()

    print("==========================================================")
    print("[EIA World Balance Skill] Executing Quarterly Balance Subplots...")
    print(f"  Force Refresh : {args.force_refresh}")
    print(f"  Date Window   : {args.start_date} to {args.end_date}")
    print(f"  Locale        : {args.locale}")
    print("==========================================================")
    
    # Initialize EIA Client
    client = EIAClient()
    
    # Fetch target series (PAPR_WORLD, PATC_WORLD, T3_STCHANGE_WORLD)
    series_ids = ['PAPR_WORLD', 'PATC_WORLD', 'T3_STCHANGE_WORLD']
    print(f"\nFetching STEO quarterly data for series: {series_ids}...")
    
    df_raw = client.get_data_steo(
        series_ids, frequency='quarterly', force_refresh=args.force_refresh
    )
    if df_raw.empty:
        print("[Error] Failed to fetch data from EIA STEO. Exiting.")
        sys.exit(1)
        
    print(f"Fetch completed. Raw dataset: {df_raw.shape[0]} quarterly observations.")
    print(f"  Date range in API: {df_raw['date'].min().strftime('%Y-%m')} to {df_raw['date'].max().strftime('%Y-%m')}")
    
    # Ensure date column is datetime
    df_raw['date'] = pd.to_datetime(df_raw['date'])
    
    # Filter to user-defined display window
    df_filtered = df_raw[
        (df_raw['date'] >= args.start_date) &
        (df_raw['date'] <= args.end_date)
    ].copy()
    df_filtered = df_filtered.sort_values(by='date').reset_index(drop=True)
    print(f"  Filtered to display window: {len(df_filtered)} quarterly observations.")
    
    if df_filtered.empty:
        print("[Error] No data found in the specified date window. Adjust --start-date / --end-date.")
        sys.exit(1)
    
    # Save refreshed wide-format CSV
    transformed_dir = os.path.join('output', 'data', 'transformed')
    os.makedirs(transformed_dir, exist_ok=True)
    csv_path = os.path.join(transformed_dir, 'eia_world_balance_quarterly.csv')
    df_filtered.to_csv(csv_path, index=False)
    print(f"  Wide-format data saved to: {csv_path}")
    
    # ---- RENDER REQUESTED LOCALES ----
    if args.locale in ('both', 'eng'):
        print("\nRendering English quarterly balance subplot chart...")
        fig_eng = build_charts(df_filtered, thai_locale=False)
        saved_eng = save_chart(fig_eng, 'eia_world_balance_quarterly.png')
        print(f"  English chart saved: {saved_eng}")
    
    if args.locale in ('both', 'thai'):
        print("\nRendering Thai quarterly balance subplot chart...")
        fig_thai = build_charts(df_filtered, thai_locale=True)
        saved_thai = save_chart(fig_thai, 'eia_world_balance_quarterly_thai.png')
        print(f"  Thai chart saved: {saved_thai}")
    
    print("\n=========================================================")
    print("[EIA World Balance Skill] All done. Update PROJECT_STATE.json registry.")
    print("==========================================================")

if __name__ == "__main__":
    main()

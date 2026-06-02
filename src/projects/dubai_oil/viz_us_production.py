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
project_root = Path(__file__).resolve().parent.parent.parent.parent
    current_yyyy_mm = datetime.now().strftime("%Y-%m")
sys.path.append(str(project_root))

from src.visualization.charts import configure_matplotlib_font, save_chart
from src.utils.registry import add_dataset, add_visualization

def main():
    print("==========================================================")
    print("[US Production Viz] Generating U.S. Crude Production Chart...")
    print("==========================================================")
    
    raw_path = project_root / "temp" / "ceic_candidates_raw.csv"
    
    # 1. Load data
    if raw_path.exists():
        print(f"Loading data from raw cache: {raw_path}")
        df = pd.read_csv(raw_path)
    else:
        print("[Error] Raw data cache not found. Attempting to fetch fresh from CEIC...")
        from src.api.ceic_client import CeicSession
        session = CeicSession()
        if session.authenticate():
            df = session.get_data(["355221677", "520147117", "43155301"])
            if df.empty:
                print("[Error] Failed to fetch data from CEIC. Exiting.")
                sys.exit(1)
            # Save raw cache
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(raw_path, index=False)
        else:
            print("[Error] Failed to authenticate with CEIC. Exiting.")
            sys.exit(1)
            
    # 2. Filter for weekly series (ID 355221677) and transform
    df['date'] = pd.to_datetime(df['date'])
    df_weekly = df[df['series_id'] == 355221677].sort_values('date').copy()
    
    if df_weekly.empty:
        print("[Error] Weekly series 355221677 data not found in cache. Exiting.")
        sys.exit(1)
        
    print(f"Loaded {len(df_weekly)} weekly observations from {df_weekly['date'].min().strftime('%Y-%m-%d')} to {df_weekly['date'].max().strftime('%Y-%m-%d')}.")
    
    # Filter recent history (Jan 2024 - May 2026)
    df_weekly_recent = df_weekly[(df_weekly['date'] >= '2024-01-01') & (df_weekly['date'] <= '2026-05-31')].copy()
    df_weekly_recent.set_index('date', inplace=True)
    
    # Resample to monthly average (Mean, aligned at Month-End)
    df_monthly = df_weekly_recent[['value']].resample('ME').mean().reset_index()
    df_monthly['value_mbd'] = df_monthly['value'] / 1000.0  # Convert to million barrels per day (mb/d)
    
    # Save transformed data
    transformed_dir = project_root / "output" / "report" / "price_forecast" / current_yyyy_mm / "data" / "transformed"
    transformed_dir.mkdir(parents=True, exist_ok=True)
    transformed_path = transformed_dir / "us_crude_production.csv"
    df_monthly.to_csv(transformed_path, index=False)
    print(f"✅ Saved transformed monthly U.S. crude production to: {transformed_path}")
    
    # Register dataset in PROJECT_STATE.json
    try:
        add_dataset(
            series_id="355221677",
            source="CEIC Global Database",
            raw_path="temp/ceic_candidates_raw.csv",
            transformed_path=f"output/report/price_forecast/{current_yyyy_mm}/data/transformed/us_crude_production.csv",
            status="Ready"
        )
    except Exception as e:
        print(f"⚠️ Failed to register dataset: {e}")
        
    # 3. Plot U.S. Crude Production Chart
    configure_matplotlib_font(font_name='FC Vision')
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    
    # Plot line
    # Primary line: deep slate or navy grey for US production
    ax.plot(
        df_monthly['date'], df_monthly['value_mbd'],
        color='#334155', linestyle='-', linewidth=2.5,
        marker='o', markersize=6.0, label='U.S. Monthly Crude Oil Production'
    )
    
    # Shade the 2025-2026 high-level plateau phase (~13.6 - 13.7 mb/d)
    # The plateau spans from mid-2025 through May 2026.
    plateau_start_date = pd.Timestamp("2025-06-01")
    plateau_end_date = pd.Timestamp("2026-05-31")
    
    ax.axvspan(
        plateau_start_date, plateau_end_date,
        color='#f1f5f9', alpha=0.7, label='Mature Plateau Phase'
    )
    
    # Add horizontal line for the plateau level (~13.6 mb/d)
    ax.axhline(y=13.6, color='#64748b', linestyle='--', linewidth=1.2, alpha=0.8)
    
    # Annotation for plateau phase
    annotation_date = pd.Timestamp("2025-11-01")
    ax.annotate(
        "Capital Discipline & Acreage Maturation\nProduction Plateaus at ~13.6 - 13.8 mb/d",
        xy=(annotation_date, 13.65),
        xytext=(annotation_date - pd.DateOffset(days=120), 13.1),
        arrowprops=dict(facecolor='#334155', shrink=0.08, width=0.8, headwidth=5, edgecolor='none'),
        color='#1e293b', fontweight='bold', fontsize=9.0, ha='center',
        bbox=dict(boxstyle="round,pad=0.3", fc="#ffffff", ec="#cbd5e1", lw=0.8, alpha=0.95)
    )
    
    # Vertical line highlighting early 2026 period
    ax.axvline(x=pd.Timestamp("2026-01-01"), color='#94a3b8', linestyle=':', linewidth=1.2)
    
    # Titles and formatting
    fig.suptitle("U.S. Monthly Crude Oil Production & Plateau Phase (2024 - 2026)", fontsize=14, fontweight='bold', x=0.5, y=0.96, ha='center')
    ax.set_title("Based on high-frequency CEIC weekly series resampled to monthly averages", fontsize=9.5, color='#64748b', pad=8, loc='center')
    
    ax.set_ylabel("Production (Million Barrels / Day)", fontsize=10.5, fontweight='bold', labelpad=8)
    ax.set_xlabel(None)
    ax.xaxis.label.set_visible(False)
    ax.set_ylim(12.0, 14.2)
    
    ax.grid(True, which='both', linestyle='-', color='#e2e8f0', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    
    ax.legend(loc='lower right', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', framealpha=0.9, fontsize=9.5)
    
    # Date formatting
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
    plt.xticks(rotation=30, ha='right')
    
    # Add source attribution
    fig.text(0.08, 0.02, "Source: CEIC Global Database, Petroleum Supply Weekly series (ID: 355221677)", fontsize=8.0, color='#64748b', ha='left', family='FC Vision')
    
    plt.tight_layout()
    fig.subplots_adjust(top=0.87, bottom=0.18)
    
    # Save figure
    out_chart_path = f"output/report/price_forecast/{current_yyyy_mm}/chart/us_crude_production.png"
    save_chart(fig, out_chart_path, save_html=False)
    print(f"✅ Successfully generated and saved US production chart to: {out_chart_path}")
    
    # Register visualization in PROJECT_STATE.json
    try:
        add_visualization(
            name="U.S. Crude Oil Production and Plateau Phase",
            chart_type="Line with Highlight Area",
            source_data=f"output/report/price_forecast/{current_yyyy_mm}/data/transformed/us_crude_production.csv",
            png_path=out_chart_path,
            status="Rendered"
        )
    except Exception as e:
        print(f"⚠️ Failed to register visualization: {e}")

if __name__ == "__main__":
    main()

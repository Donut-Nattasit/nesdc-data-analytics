import os
import sys
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.visualization.charts import configure_matplotlib_font, save_chart

def main():
    print("==========================================================")
    print("[Dubai Oil Viz] Generating Professional Line Chart...")
    print("==========================================================")
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    data_path = project_root / "output" / "data" / "energy_price_forecast" / "dubai_oil_forecast_production.csv"
    
    if not data_path.exists():
        print(f"[Error] Production forecast dataset not found at: {data_path}")
        sys.exit(1)
        
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # 1. Filter data starting from Jan 2024 to Dec 2027
    df_filtered = df[(df['date'] >= '2024-01-01') & (df['date'] <= '2027-12-01')].copy().reset_index(drop=True)
    
    # Configure C-suite styling and font
    configure_matplotlib_font(font_name='FC Vision')
    
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    
    # Find forecast origin dynamically (the latest month where actual spot data is available)
    forecast_origin = df_filtered[df_filtered['dubai_spot'].notna()]['date'].max()
    print(f"  Forecast Origin (Last Actual Month): {forecast_origin.strftime('%Y-%m-%d')}")
    df_hist = df_filtered[df_filtered['date'] <= forecast_origin].copy()
    
    # Separate future forecasts (starts at forecast origin to connect smoothly with history)
    df_fc = df_filtered[df_filtered['date'] >= forecast_origin].copy()
    
    # 2. Plotting the lines
    # Line A: Historical Spot Price
    ax.plot(
        df_hist['date'], df_hist['dubai_spot'],
        color='#475569', linestyle='-', linewidth=2.5,
        marker='o', markersize=4, label='Historical Spot Dubai (GIOS0097)'
    )
    
    # Line B: Error Correction Model (ECM) Forecast Trajectory
    ax.plot(
        df_fc['date'], df_fc['dubai_spot_forecast'],
        color='#00109E', linestyle='-', linewidth=3.0,
        marker='o', markersize=5, label='Official ECM Forecast'
    )
    
    # Line C: Raw Futures Curve (Traded Consensus)
    # We use dubai_baseline for the forecast period (which starts at forecast_origin)
    ax.plot(
        df_fc['date'], df_fc['dubai_baseline'],
        color='#b45309', linestyle='--', linewidth=2.0,
        marker='s', markersize=4, label=f'Raw Futures Curve (Priced {forecast_origin.strftime("%B %Y")})'
    )
    
    # 3. Add Key Details and Formatting
    # Add vertical line at forecast origin
    ax.axvline(x=forecast_origin, color='#94a3b8', linestyle=':', linewidth=1.5)
    ax.text(
        forecast_origin + pd.DateOffset(days=10), 105,
        f'Forecast Origin\n({forecast_origin.strftime("%b %Y")})',
        color='#64748b', fontsize=10, fontweight='bold', ha='left'
    )
    
    # Titles and labels
    ax.set_title("Dubai Crude Oil Price: Historical & Projections to 2027", fontsize=16, fontweight='bold', pad=15)
    ax.set_ylabel("Price (USD / Barrel)", fontsize=12, fontweight='bold', labelpad=10)
    ax.set_xlabel("Date", fontsize=12, fontweight='bold', labelpad=10)
    
    # Customize grid and spines
    ax.grid(True, which='both', linestyle='-', color='#e2e8f0', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    
    # Legend
    ax.legend(loc='lower left', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', framealpha=0.9, fontsize=10)
    
    # X-axis date formatting
    import matplotlib.dates as mdates
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
    plt.xticks(rotation=45)
    
    # Annotate final values for clarity
    final_ecm_val = df_fc.iloc[-1]['dubai_spot_forecast']
    final_future_val = df_fc.iloc[-1]['dubai_baseline']
    final_date = df_fc.iloc[-1]['date']
    
    ax.annotate(
        f"ECM Forecast: ${final_ecm_val:.2f}",
        xy=(final_date, final_ecm_val),
        xytext=(final_date - pd.DateOffset(months=4), final_ecm_val - 4),
        arrowprops=dict(facecolor='#00109E', shrink=0.08, width=1, headwidth=6),
        color='#00109E', fontweight='bold', fontsize=10
    )
    
    ax.annotate(
        f"Futures: ${final_future_val:.2f}",
        xy=(final_date, final_future_val),
        xytext=(final_date - pd.DateOffset(months=4), final_future_val + 3),
        arrowprops=dict(facecolor='#b45309', shrink=0.08, width=1, headwidth=6),
        color='#b45309', fontweight='bold', fontsize=10
    )
    
    plt.tight_layout()
    
    # 4. Save figure using standard viz engine
    out_path = "output/chart/energy_price_forecast/dubai_oil_forecast_comparison.png"
    # Ensure subdirectory exists
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    save_chart(fig, out_path, save_html=False)
    print("Successfully generated and saved line chart!")
    
if __name__ == "__main__":
    main()

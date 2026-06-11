import os
import sys
import sqlite3
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from pathlib import Path

# Override print to automatically flush stdout for background log visibility
_print = print
def print(*args, **kwargs):
    _print(*args, **kwargs)
    sys.stdout.flush()

warnings.filterwarnings("ignore")

# Define root and path constants
ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(ROOT))

from src.utils.registry import add_dataset, add_visualization

# Output directories
DATA_IN_DIR = ROOT / "output" / "data" / "cpi_forecast"
OUT_DATA_DIR = ROOT / "output" / "data" / "prepared_food_shock"
OUT_CHART_DIR = ROOT / "output" / "chart" / "prepared_food_shock"
DB_DIR = ROOT / "database" / "prepared_food_shock"

OUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
OUT_CHART_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

# Styling constants matching viz-playbook
WATERMARK = "Source: CEIC API, MOC, & NESDC Shock Scenario Model"

def apply_style(ax):
    ax.grid(True, linestyle="--", alpha=0.25, color="#cccccc")
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(axis="both", labelsize=9, colors="#2c3e50")

def shade_forecast(ax, df_plot):
    fc_start = pd.Timestamp("2026-06-01")
    sep = fc_start - pd.Timedelta(days=15)
    ax.axvline(sep, color="#FFA300", linestyle="--", linewidth=1.2, alpha=0.8)
    ax.axvspan(sep, df_plot.index.max(), color="#f8fafc", alpha=0.9, zorder=0)
    ylim = ax.get_ylim()
    y_pos = ylim[0] + (ylim[1] - ylim[0]) * 0.92
    ax.text(fc_start + pd.Timedelta(days=10), y_pos, "FORECAST SHOCK",
            color="#FFA300", fontweight="bold", fontsize=8, alpha=0.8)

def save(fig, name, tight=True, rect=None):
    path = OUT_CHART_DIR / name
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
    print(f"  [OK] Saved chart: {path.name}")
    return path

def main():
    print("==========================================================")
    print("  NESDC Prepared Food CPI Shock Scenario Analysis Script")
    print("==========================================================")
    
    # 1. Load baseline monthly forecast data
    cpi_fc_path = DATA_IN_DIR / "cpi_forecast_monthly.csv"
    if not cpi_fc_path.exists():
        print(f"[FAIL] Baseline monthly forecast not found at: {cpi_fc_path}")
        print("Please run the cpi_forecast pipeline first.")
        sys.exit(1)
        
    df = pd.read_csv(cpi_fc_path, index_col='date', parse_dates=True).sort_index()
    print(f"Loaded monthly forecast data. Date range: {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
    
    # Separate history and forecast
    hist = df[df['is_forecast'] == 0].copy()
    fc = df[df['is_forecast'] == 1].copy()
    
    # 2. Calibrate Prepared Food Shock based on 2022 actuals
    # Historical levels of Prepared Food in 2022:
    # Jan 2022: 91.35, Feb 2022: 95.30, Mar 2022: 95.88, Apr 2022: 96.10, May 2022: 96.29,
    # Jun 2022: 96.66, Jul 2022: 98.16, Aug 2022: 98.29, Sep 2022: 98.66, Oct 2022: 98.78,
    # Nov 2022: 99.09, Dec 2022: 99.30.
    mom_2022 = [
        (95.30 / 91.35) - 1,  # Month 1 (Feb 2022)
        (95.88 / 95.30) - 1,  # Month 2 (Mar 2022)
        (96.10 / 95.88) - 1,  # Month 3 (Apr 2022)
        (96.29 / 96.10) - 1,  # Month 4 (May 2022)
        (96.66 / 96.29) - 1,  # Month 5 (Jun 2022)
        (98.16 / 96.66) - 1,  # Month 6 (Jul 2022)
        (98.29 / 98.16) - 1,  # Month 7 (Aug 2022)
        (98.66 / 98.29) - 1,  # Month 8 (Sep 2022)
        (98.78 / 98.66) - 1,  # Month 9 (Oct 2022)
        (99.09 / 98.78) - 1,  # Month 10 (Nov 2022)
        (99.30 / 99.09) - 1,  # Month 11 (Dec 2022)
    ]
    
    # Scale shock by 1.5x (Dampened scaling option confirmed via /grill-me)
    scale_factor = 1.5
    shocked_mom = [r * scale_factor for r in mom_2022]
    
    print(f"Calibrated Shock Profile: Dampened Scaling ({scale_factor}x)")
    print(f"  Initial MoM Jump: {shocked_mom[0]*100:.2f}% (vs. baseline history 2022: {mom_2022[0]*100:.2f}%)")
    print(f"  Subsequent MoM Shock decay array size: {len(shocked_mom)-1} months")
    
    # Apply to forecast period starting June 2026
    # May 2026 level = 106.75 (historical actual)
    last_hist_val = hist['index_Prepared_Food'].dropna().iloc[-1]
    last_hist_date = hist.index.max()
    print(f"  May 2026 (last actual) Prepared Food index level: {last_hist_val:.2f}")
    
    shocked_pf = []
    current_val = last_hist_val
    baseline_mom_fc = fc['index_Prepared_Food'].pct_change()
    
    for i, date in enumerate(fc.index):
        if i < len(shocked_mom):
            # Apply shock MoM growth
            current_val = current_val * (1 + shocked_mom[i])
        else:
            # Revert to baseline forecast growth rate
            baseline_grow = baseline_mom_fc.iloc[i]
            if pd.isna(baseline_grow):
                # Fallback if first row NaN
                baseline_grow = 0.001
            current_val = current_val * (1 + baseline_grow)
        shocked_pf.append(current_val)
        
    fc['index_Prepared_Food_shock'] = shocked_pf
    hist['index_Prepared_Food_shock'] = hist['index_Prepared_Food']
    
    # Merge history and forecast back together
    df_shock = pd.concat([hist, fc], axis=0).sort_index()
    
    # 3. Re-aggregate CPI composites under shock
    core_components = [
        "Seasoning_Condiments", "Non_Alcoholic_Beverages", "Sugar_Product", "Prepared_Food",
        "Apparel_Footwears", "Housing_Furnishing_ex_Utility", "Medical_Personal_Care",
        "Transport_Communication_ex_Motor_Fuel", "Recreation_Reading_Education_Religion",
        "Tobacco_Alcoholic_Beverages"
    ]
    raw_food_components = ["Rice_Flour_Cereal", "Meats_Poultry_Fish", "Eggs_Dairy_Products", "Vegetables_Fruits"]
    energy_components = ["Housing_Furnishing_Utility", "Transport_Communication_Motor_Fuel"]
    all_components = core_components + raw_food_components + energy_components
    
    def calculate_weighted_composite_shock(df, components):
        w_cols = [f"weight_{c}" for c in components]
        weight_sum = df[w_cols].sum(axis=1)
        weighted_sum = 0
        for c in components:
            idx_col = f"index_{c}_shock" if c == "Prepared_Food" else f"index_{c}"
            weighted_sum += df[idx_col] * df[f"weight_{c}"]
        return weighted_sum / weight_sum
        
    df_shock['Core_CPI_shock'] = calculate_weighted_composite_shock(df_shock, core_components)
    df_shock['Headline_CPI_shock'] = calculate_weighted_composite_shock(df_shock, all_components)
    
    # Compute YoY growth rates
    df_shock['Prepared_Food_YoY_baseline'] = df_shock['index_Prepared_Food'].pct_change(12) * 100
    df_shock['Prepared_Food_YoY_shock'] = df_shock['index_Prepared_Food_shock'].pct_change(12) * 100
    df_shock['Core_YoY_baseline'] = df_shock['Core_CPI'].pct_change(12) * 100
    df_shock['Core_YoY_shock'] = df_shock['Core_CPI_shock'].pct_change(12) * 100
    df_shock['Headline_YoY_baseline'] = df_shock['Headline_CPI'].pct_change(12) * 100
    df_shock['Headline_YoY_shock'] = df_shock['Headline_CPI_shock'].pct_change(12) * 100
    
    # 4. Save comparison dataset (CSV & SQLite)
    df_comparison = df_shock[[
        'index_Prepared_Food', 'index_Prepared_Food_shock',
        'Prepared_Food_YoY_baseline', 'Prepared_Food_YoY_shock',
        'Core_CPI', 'Core_CPI_shock',
        'Core_YoY_baseline', 'Core_YoY_shock',
        'Headline_CPI', 'Headline_CPI_shock',
        'Headline_YoY_baseline', 'Headline_YoY_shock',
        'is_forecast'
    ]].rename(columns={
        'index_Prepared_Food': 'Prepared_Food_Index_baseline',
        'index_Prepared_Food_shock': 'Prepared_Food_Index_shock',
        'Core_CPI': 'Core_CPI_baseline',
        'Headline_CPI': 'Headline_CPI_baseline'
    })
    
    csv_out_path = OUT_DATA_DIR / "prepared_food_shock_comparison.csv"
    df_comparison.to_csv(csv_out_path, index=True, index_label='date')
    print(f"[OK] Saved comparison CSV to: {csv_out_path}")
    
    # 4b. Calculate Annual Average YoY Growth rates
    print("\nCalculating Annual Average YoY Growth rates...")
    idx_cols = [
        'Prepared_Food_Index_baseline', 'Prepared_Food_Index_shock',
        'Core_CPI_baseline', 'Core_CPI_shock',
        'Headline_CPI_baseline', 'Headline_CPI_shock'
    ]
    df_annual_idx = df_comparison[idx_cols].resample('YE').mean()
    df_annual_growth = df_annual_idx.pct_change() * 100
    df_annual_growth = df_annual_growth.rename(columns={
        'Prepared_Food_Index_baseline': 'Prepared_Food_Annual_YoY_baseline',
        'Prepared_Food_Index_shock': 'Prepared_Food_Annual_YoY_shock',
        'Core_CPI_baseline': 'Core_Annual_YoY_baseline',
        'Core_CPI_shock': 'Core_Annual_YoY_shock',
        'Headline_CPI_baseline': 'Headline_Annual_YoY_baseline',
        'Headline_CPI_shock': 'Headline_Annual_YoY_shock'
    }).loc['2021-01-01':]
    
    csv_annual_path = OUT_DATA_DIR / "prepared_food_shock_annual_growth.csv"
    df_annual_growth.to_csv(csv_annual_path, index=True, index_label='year')
    print(f"[OK] Saved annual growth CSV to: {csv_annual_path}")
    
    db_out_path = DB_DIR / "prepared_food_shock.db"
    conn = sqlite3.connect(str(db_out_path))
    try:
        # Save monthly comparison
        df_db_write = df_comparison.copy()
        df_db_write.index = df_db_write.index.strftime('%Y-%m-%d')
        df_db_write.to_sql("prepared_food_shock_comparison", conn, if_exists="replace", index=True, index_label='date')
        
        # Save annual growth comparison
        df_annual_db = df_annual_growth.copy()
        df_annual_db.index = df_annual_db.index.strftime('%Y')
        df_annual_db.to_sql("prepared_food_shock_annual_growth", conn, if_exists="replace", index=True, index_label='year')
        
        conn.commit()
        print(f"[OK] Exported datasets to SQLite database: {db_out_path} (tables: prepared_food_shock_comparison, prepared_food_shock_annual_growth)")
    except Exception as e:
        print(f"[Warning] Failed to write database: {e}")
    finally:
        conn.close()
        
    # Register datasets in PROJECT_STATE.json
    add_dataset(
        series_id="Prepared Food CPI Shock Scenario Comparison",
        source="MOC & NESDC Geopolitical Shock Simulation",
        raw_path="output/data/cpi_forecast/cpi_forecast_monthly.csv",
        transformed_path="output/data/prepared_food_shock/prepared_food_shock_comparison.csv",
        forecast_path="",
        status="Ready"
    )
    add_dataset(
        series_id="Prepared Food CPI Shock Annual Growth Comparison",
        source="MOC & NESDC Geopolitical Shock Simulation",
        raw_path="output/data/prepared_food_shock/prepared_food_shock_comparison.csv",
        transformed_path="output/data/prepared_food_shock/prepared_food_shock_annual_growth.csv",
        forecast_path="",
        status="Ready"
    )
    
    # 5. Generate Comparison Plots
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Inter', 'DejaVu Sans', 'Arial']
    
    # Chart 1: Prepared Food CPI Index Levels
    print("\nPlotting Chart 1: Prepared Food Index Level Comparison...")
    fig, ax = plt.subplots(figsize=(10, 5), dpi=180)
    # Slice from 2021 for readability
    df_plot = df_comparison.loc["2021-01-01":]
    hist_plot = df_plot[df_plot['is_forecast'] == 0]
    fc_plot = df_plot[df_plot['is_forecast'] == 1]
    
    ax.plot(hist_plot.index, hist_plot['Prepared_Food_Index_baseline'], color="#2c3e50", linewidth=2.0, label="Historical Actual")
    ax.plot(fc_plot.index, fc_plot['Prepared_Food_Index_baseline'], color="#7f8c8d", linewidth=1.8, linestyle="--", label="Baseline Forecast (Linear auto_ARIMA)")
    ax.plot(fc_plot.index, fc_plot['Prepared_Food_Index_shock'], color="#d35400", linewidth=2.2, label="Shock Forecast (1.5x Russia-Ukraine Analogy)")
    
    ax.set_title("Prepared Food CPI Index Level Scenario Comparison (2021–2027)", fontsize=12, fontweight="bold", pad=12, color="#2c3e50")
    ax.set_ylabel("Index Level (2019 = 100)", fontsize=10, color="#2c3e50")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="lower right", fontsize=8.5, frameon=True, facecolor="white", edgecolor="none")
    shade_forecast(ax, df_plot)
    apply_style(ax)
    chart1_path = save(fig, "prepared_food_index_comparison.png")
    
    # Chart 2: Prepared Food YoY Growth Rates
    print("Plotting Chart 2: Prepared Food YoY Growth Comparison...")
    fig, ax = plt.subplots(figsize=(10, 5), dpi=180)
    ax.plot(hist_plot.index, hist_plot['Prepared_Food_YoY_baseline'], color="#2c3e50", linewidth=2.0, label="Historical Actual")
    ax.plot(fc_plot.index, fc_plot['Prepared_Food_YoY_baseline'], color="#7f8c8d", linewidth=1.8, linestyle="--", label="Baseline Forecast")
    ax.plot(fc_plot.index, fc_plot['Prepared_Food_YoY_shock'], color="#d35400", linewidth=2.2, label="Shock Forecast")
    
    ax.set_title("Prepared Food CPI YoY Growth Scenario Comparison (2021–2027)", fontsize=12, fontweight="bold", pad=12, color="#2c3e50")
    ax.set_ylabel("YoY Growth (%)", fontsize=10, color="#2c3e50")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper left", fontsize=8.5, frameon=True, facecolor="white", edgecolor="none")
    shade_forecast(ax, df_plot)
    apply_style(ax)
    chart2_path = save(fig, "prepared_food_yoy_comparison.png")
    
    # Chart 3: Aggregate Impact (Headline vs. Core YoY)
    print("Plotting Chart 3: Headline and Core CPI aggregate impact...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9), dpi=180, sharex=True)
    
    # Headline CPI YoY
    ax1.plot(hist_plot.index, hist_plot['Headline_YoY_baseline'], color="#2c3e50", linewidth=1.8, label="Historical Actual")
    ax1.plot(fc_plot.index, fc_plot['Headline_YoY_baseline'], color="#64748b", linewidth=1.6, linestyle="--", label="Baseline Forecast")
    ax1.plot(fc_plot.index, fc_plot['Headline_YoY_shock'], color="#00109E", linewidth=2.0, label="Shock Forecast (Iran War Scenario)")
    ax1.set_ylabel("Headline Inflation (YoY %)", fontsize=9.5, color="#2c3e50")
    ax1.set_title("Headline CPI Inflation Impact (YoY %)", fontsize=10.5, fontweight="bold", color="#2c3e50", loc="left")
    ax1.legend(loc="upper left", fontsize=8, frameon=True, facecolor="white", edgecolor="none")
    shade_forecast(ax1, df_plot)
    apply_style(ax1)
    
    # Core CPI YoY
    ax2.plot(hist_plot.index, hist_plot['Core_YoY_baseline'], color="#2c3e50", linewidth=1.8, label="Historical Actual")
    ax2.plot(fc_plot.index, fc_plot['Core_YoY_baseline'], color="#64748b", linewidth=1.6, linestyle="--", label="Baseline Forecast")
    ax2.plot(fc_plot.index, fc_plot['Core_YoY_shock'], color="#60B1E7", linewidth=2.0, label="Shock Forecast (Iran War Scenario)")
    ax2.set_ylabel("Core Inflation (YoY %)", fontsize=9.5, color="#2c3e50")
    ax2.set_title("Core CPI Inflation Impact (YoY %)", fontsize=10.5, fontweight="bold", color="#2c3e50", loc="left")
    ax2.legend(loc="upper left", fontsize=8, frameon=True, facecolor="white", edgecolor="none")
    shade_forecast(ax2, df_plot)
    apply_style(ax2)
    
    fig.suptitle("Inflation Impact of Prepared Food Shock — Baseline vs. Iran War Scenario", fontsize=13, fontweight="bold", y=0.97, color="#2c3e50")
    fig.autofmt_xdate(rotation=0)
    chart3_path = save(fig, "cpi_aggregates_yoy_comparison.png", rect=[0, 0.04, 1, 0.93])
    
    # Register Visualizations
    add_visualization(
        name="Prepared Food Index Comparison",
        chart_type="Line Chart",
        source_data="prepared_food_shock_comparison.csv",
        png_path="output/chart/prepared_food_shock/prepared_food_index_comparison.png"
    )
    add_visualization(
        name="Prepared Food YoY Comparison",
        chart_type="Line Chart",
        source_data="prepared_food_shock_comparison.csv",
        png_path="output/chart/prepared_food_shock/prepared_food_yoy_comparison.png"
    )
    add_visualization(
        name="CPI Aggregates YoY Comparison",
        chart_type="Multi-Panel Line Chart",
        source_data="prepared_food_shock_comparison.csv",
        png_path="output/chart/prepared_food_shock/cpi_aggregates_yoy_comparison.png"
    )
    
    print("\nAnalysis phase completed successfully!")

if __name__ == "__main__":
    main()

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# Override print to automatically flush stdout for background log visibility
_print = print
def print(*args, **kwargs):
    _print(*args, **kwargs)
    sys.stdout.flush()

# Add project root to sys.path to allow src imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from src.utils.registry import add_visualization

def plot_cpi_series(df, columns, title, filename, output_dir, colors=None, start_date="2021-01-01"):
    # Filter to display range
    df_plot = df.loc[start_date:].copy()
    
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    
    # Grid lines
    ax.grid(True, linestyle="--", alpha=0.3, color="#cccccc")
    
    # Plot lines
    if colors:
        for col, color in zip(columns, colors):
            label = col.replace("index_", "").replace("_", " ")
            linewidth = 3 if "CPI" in col or col == "Headline_CPI" else 1.8
            ax.plot(df_plot.index, df_plot[col], label=label, linewidth=linewidth, color=color)
    else:
        # Generate distinct colors for many components
        cmap = plt.get_cmap("tab20")
        for i, col in enumerate(columns):
            label = col.replace("index_", "").replace("_", " ")
            ax.plot(df_plot.index, df_plot[col], label=label, linewidth=1.8, color=cmap(i % 20))
            
    # Highlight the Forecast region
    forecast_start = pd.to_datetime("2026-06-01")
    if forecast_start in df_plot.index:
        ax.axvline(forecast_start - pd.Timedelta(days=15), color="#e74c3c", linestyle="--", linewidth=1.5, alpha=0.8)
        ax.axvspan(forecast_start - pd.Timedelta(days=15), df_plot.index.max(), color="#f5f6fa", alpha=0.9, label="Forecast Period")
        
        # Add text label for forecast
        y_limits = ax.get_ylim()
        y_pos = y_limits[0] + (y_limits[1] - y_limits[0]) * 0.9
        ax.text(forecast_start + pd.Timedelta(days=10), y_pos, "FORECAST", color="#e74c3c", fontweight="bold", fontsize=10, alpha=0.8)

    # Style labels and titles
    ax.set_title(title, fontsize=15, fontweight="bold", pad=15, color="#2c3e50")
    ax.set_ylabel("Index Value (2023 = 100)", fontsize=11, fontweight="bold", color="#2c3e50")
    ax.set_xlabel("Date", fontsize=11, fontweight="bold", color="#2c3e50")
    
    # Format X axis
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=3))
    
    # Clean spines
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    
    # Legend
    ax.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="none", shadow=True, fontsize=10)
    
    # Watermark
    ax.text(0.99, 0.01, "Source: CEIC API & NESDC auto_ARIMA Forecast Model", 
            transform=ax.transAxes, fontsize=8, color="#7f8c8d", alpha=0.7, ha="right")
            
    plt.tight_layout()
    
    # Save chart
    out_path = output_dir / filename
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Rendered and saved chart: {out_path}")

def main():
    print("==========================================================")
    print("[CPI Visualization] Generating forecast line charts...")
    print("==========================================================")
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    data_path = project_root / "output" / "data" / "cpi_forecast" / "cpi_forecast_monthly.csv"
    chart_out_dir = project_root / "output" / "chart" / "cpi_forecast"
    chart_out_dir.mkdir(parents=True, exist_ok=True)
    
    if not data_path.exists():
        print(f"[FAIL] Ingested forecast data not found at: {data_path}")
        raise RuntimeError("Pipeline step failed")
        
    # Read monthly data
    df = pd.read_csv(data_path, index_col='date', parse_dates=True).sort_index()
    
    # 1. Plot Composite Aggregates
    composite_cols = ["Headline_CPI", "Core_CPI", "Raw_Food_CPI", "Energy_CPI"]
    # Curated premium colors
    comp_colors = ["#2c3e50", "#2980b9", "#27ae60", "#c0392b"]
    plot_cpi_series(
        df=df,
        columns=composite_cols,
        title="Thailand Consumer Price Index (CPI): Composites Forecast",
        filename="cpi_composite_forecast.png",
        output_dir=chart_out_dir,
        colors=comp_colors
    )
    
    # 2. Plot Core Components (10 variables)
    core_components = [
        "index_Seasoning_Condiments", "index_Non_Alcoholic_Beverages", "index_Sugar_Product",
        "index_Prepared_Food", "index_Apparel_Footwears", "index_Housing_Furnishing_ex_Utility",
        "index_Medical_Personal_Care", "index_Transport_Communication_ex_Motor_Fuel",
        "index_Recreation_Reading_Education_Religion", "index_Tobacco_Alcoholic_Beverages"
    ]
    plot_cpi_series(
        df=df,
        columns=core_components,
        title="CPI Components: Core CPI Items Forecast",
        filename="cpi_core_components_forecast.png",
        output_dir=chart_out_dir
    )
    
    # 3. Plot Non-Core Components (6 variables)
    non_core_components = [
        "index_Rice_Flour_Cereal", "index_Meats_Poultry_Fish", "index_Eggs_Dairy_Products",
        "index_Vegetables_Fruits", "index_Housing_Furnishing_Utility", "index_Transport_Communication_Motor_Fuel"
    ]
    plot_cpi_series(
        df=df,
        columns=non_core_components,
        title="CPI Components: Non-Core (Raw Food & Energy) Items Forecast",
        filename="cpi_non_core_components_forecast.png",
        output_dir=chart_out_dir
    )
    
    # 4. Register Visualizations in PROJECT_STATE.json
    try:
        add_visualization(
            name="CPI Composite Forecast",
            chart_type="Line Chart",
            source_data="output/data/cpi_forecast/cpi_forecast_monthly.csv",
            png_path="output/chart/cpi_forecast/cpi_composite_forecast.png",
            status="Rendered"
        )
        add_visualization(
            name="CPI Core Components Forecast",
            chart_type="Line Chart",
            source_data="output/data/cpi_forecast/cpi_forecast_monthly.csv",
            png_path="output/chart/cpi_forecast/cpi_core_components_forecast.png",
            status="Rendered"
        )
        add_visualization(
            name="CPI Non-Core Components Forecast",
            chart_type="Line Chart",
            source_data="output/data/cpi_forecast/cpi_forecast_monthly.csv",
            png_path="output/chart/cpi_forecast/cpi_non_core_components_forecast.png",
            status="Rendered"
        )
        print("[OK] Registered charts in PROJECT_STATE.json.")
    except Exception as e:
        print(f"[Warning] Failed to update visualizations in registry: {e}")

if __name__ == "__main__":
    main()

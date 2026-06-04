import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from src.visualization.charts import configure_matplotlib_font
from src.utils.registry import add_model, add_visualization

# Setup styling
configure_matplotlib_font('FC Vision')
plt.rcParams['figure.facecolor'] = '#FFFFFF'
plt.rcParams['axes.facecolor'] = '#FFFFFF'
plt.rcParams['grid.color'] = '#E9ECEF'
plt.rcParams['grid.alpha'] = 0.7

def main():
    print("Loading datasets...")
    # Load historical wide monthly dataset
    df_wide = pd.read_csv("output/data/export_import_monthly_wide.csv", index_col=0, parse_dates=True).sort_index()
    
    # Load forecasted monthly dataset
    forecast_path = "output/data/forecast/export_import_forecast_statsforecast.csv"
    if not os.path.exists(forecast_path):
        print(f"Error: {forecast_path} not found. Please run the forecasting scripts first.")
        sys.exit(1)
        
    df_fc = pd.read_csv(forecast_path, index_col=0, parse_dates=True).sort_index()
    
    # Ensure all required historical columns are in df_wide
    hist_cols = [
        "bot_export_price_index", 
        "bot_import_price_index", 
        "bot_export_value_index", 
        "bot_import_value_index", 
        "bot_export_quantity_index", 
        "bot_import_quantity_index"
    ]
    for col in hist_cols:
        if col not in df_wide.columns:
            print(f"Error: {col} not found in historical dataset. Please run prepare_data.py first.")
            sys.exit(1)
            
    # Check if value and quantity forecasts are present in df_fc
    if "bot_export_value_index" not in df_fc.columns or "bot_import_value_index" not in df_fc.columns:
        print("\nValue and Quantity forecasts not found in forecast dataset. Generating them dynamically...")
        import pmdarima as pm
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        
        # Fit and forecast export value index
        print("Fitting Auto-ARIMA for bot_export_value_index...")
        val_ex_hist = df_wide["bot_export_value_index"].dropna()
        model_ex = pm.auto_arima(val_ex_hist, seasonal=True, m=12, d=1, D=1, trace=False, error_action='ignore', suppress_warnings=True)
        ex_val_fit = SARIMAX(val_ex_hist, order=model_ex.order, seasonal_order=model_ex.seasonal_order).fit(disp=False)
        fc_ex_val = ex_val_fit.forecast(steps=len(df_fc))
        
        # Fit and forecast import value index
        print("Fitting Auto-ARIMA for bot_import_value_index...")
        val_im_hist = df_wide["bot_import_value_index"].dropna()
        model_im = pm.auto_arima(val_im_hist, seasonal=True, m=12, d=1, D=1, trace=False, error_action='ignore', suppress_warnings=True)
        im_val_fit = SARIMAX(val_im_hist, order=model_im.order, seasonal_order=model_im.seasonal_order).fit(disp=False)
        fc_im_val = im_val_fit.forecast(steps=len(df_fc))
        
        df_fc["bot_export_value_index"] = fc_ex_val.values
        df_fc["bot_import_value_index"] = fc_im_val.values
        
        # Compute quantity indices: Q = (V / P) * 100
        df_fc["bot_export_quantity_index"] = (df_fc["bot_export_value_index"] / df_fc["bot_export_price_index"]) * 100
        df_fc["bot_import_quantity_index"] = (df_fc["bot_import_value_index"] / df_fc["bot_import_price_index"]) * 100
        
        # Save back to CSV
        df_fc.to_csv(forecast_path)
        print("Saved generated value and quantity forecasts to statsforecast CSV.")

    # Concatenate historical and forecast data
    print("Concatenating historical and forecast monthly data...")
    df_monthly_hist = df_wide[hist_cols].dropna()
    df_monthly_fc = df_fc[hist_cols]
    df_monthly_all = pd.concat([df_monthly_hist, df_monthly_fc]).sort_index()
    
    # ------------------ 1. Resample to Quarterly ------------------
    print("\nResampling to Quarterly frequency (volume-weighted)...")
    # Resample values and quantities using mean
    df_q = df_monthly_all.resample('QE').mean()
    # Calculate volume-weighted price indices: P = (V / Q) * 100
    df_q["bot_export_price_index"] = (df_q["bot_export_value_index"] / df_q["bot_export_quantity_index"]) * 100
    df_q["bot_import_price_index"] = (df_q["bot_import_value_index"] / df_q["bot_import_quantity_index"]) * 100
    
    # Save quarterly dataset
    q_out_path = "output/data/forecast/export_import_forecast_quarterly.csv"
    df_q.to_csv(q_out_path)
    print(f"Saved quarterly aggregated dataset to {q_out_path} (Shape: {df_q.shape})")
    
    # ------------------ 2. Resample to Annual ------------------
    print("\nResampling to Annual frequency (volume-weighted)...")
    # Resample values and quantities using mean (handle pandas version compat)
    try:
        df_a = df_monthly_all.resample('YE').mean()
    except ValueError:
        df_a = df_monthly_all.resample('A').mean()
        
    # Calculate volume-weighted price indices
    df_a["bot_export_price_index"] = (df_a["bot_export_value_index"] / df_a["bot_export_quantity_index"]) * 100
    df_a["bot_import_price_index"] = (df_a["bot_import_value_index"] / df_a["bot_import_quantity_index"]) * 100
    
    # Save annual dataset
    a_out_path = "output/data/forecast/export_import_forecast_annual.csv"
    df_a.to_csv(a_out_path)
    print(f"Saved annual aggregated dataset to {a_out_path} (Shape: {df_a.shape})")
    
    # ------------------ 3. Plot Aggregations ------------------
    print("\nPlotting aggregations...")
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    plot_start_date = "2000-01-01"
    
    # Export Price Index Aggregation Plot
    ax = axes[0]
    m_data = df_monthly_all.loc[plot_start_date:]
    q_data = df_q.loc[plot_start_date:]
    a_data = df_a.loc[plot_start_date:]
    
    ax.plot(m_data.index, m_data["bot_export_price_index"], label="Monthly Price Index", color="#2B2D42", alpha=0.4, linewidth=1)
    ax.plot(q_data.index, q_data["bot_export_price_index"], label="Quarterly Price Index (Volume-Weighted)", color="#00109E", linewidth=2, marker='o', markersize=4, linestyle="--")
    ax.plot(a_data.index, a_data["bot_export_price_index"], label="Annual Price Index (Volume-Weighted)", color="#78DED4", linewidth=3, marker='s', markersize=6)
    ax.axvline(pd.to_datetime("2026-04-01"), color="red", linestyle=":", label="Forecast Start (May 2026)", alpha=0.8)
    
    ax.set_title("BOT Export Price Index: Frequency Aggregations", fontsize=13, fontweight="bold", pad=12)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper left", frameon=True, fontsize=10)
    
    # Import Price Index Aggregation Plot
    ax = axes[1]
    ax.plot(m_data.index, m_data["bot_import_price_index"], label="Monthly Price Index", color="#2B2D42", alpha=0.4, linewidth=1)
    ax.plot(q_data.index, q_data["bot_import_price_index"], label="Quarterly Price Index (Volume-Weighted)", color="#FFA300", linewidth=2, marker='o', markersize=4, linestyle="--")
    ax.plot(a_data.index, a_data["bot_import_price_index"], label="Annual Price Index (Volume-Weighted)", color="#BFB997", linewidth=3, marker='s', markersize=6)
    ax.axvline(pd.to_datetime("2026-04-01"), color="red", linestyle=":", label="Forecast Start (May 2026)", alpha=0.8)
    
    ax.set_title("BOT Import Price Index: Frequency Aggregations", fontsize=13, fontweight="bold", pad=12)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper left", frameon=True, fontsize=10)
    
    plt.tight_layout()
    chart_path = "output/chart/forecast_resampled_composites.png"
    plt.savefig(chart_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved frequency aggregation chart to {chart_path}")
    
    # Write a small summary file
    summary_path = "output/model/forecast_resampled_summary.md"
    print(f"Writing summary to {summary_path}...")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# BOT Official Price Indices: Quarterly & Annual Aggregations\n\n")
        f.write("This document details the volume-weighted resampling of monthly Export and Import Price Indices to Quarterly and Annual frequencies.\n\n")
        f.write("## 🔗 Methodology: Volume-Weighted Resampling\n")
        f.write("Rather than using simple arithmetic averages (which fail to account for monthly variation in export/import trade volumes), we resample using the **volume-weighted formula** standard in national accounting:\n\n")
        f.write("$$P_{\\text{resampled}} = \\frac{\\text{Mean Value Index}}{\\text{Mean Quantity Index}} \\times 100 = \\frac{\\sum (P_m \\times Q_m)}{\\sum Q_m}$$\n\n")
        f.write("where $P_m$ is the monthly Price Index, and $Q_m$ is the monthly Quantity Index serving as the volume weights.\n\n")
        
        # Write quarterly table
        f.write("## 📅 Quarterly Projections (Volume-Weighted)\n\n")
        f.write("| Quarter | Export Price Index | Import Price Index | Export Value | Import Value | Export Quantity | Import Quantity |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        fc_q = df_q.loc["2026-06-30":]
        for idx, row in fc_q.iterrows():
            # Format quarter name (e.g. 2026Q2)
            q_name = f"{idx.year}Q{idx.quarter}"
            f.write(f"| {q_name} | {row['bot_export_price_index']:.4f} | {row['bot_import_price_index']:.4f} | {row['bot_export_value_index']:.4f} | {row['bot_import_value_index']:.4f} | {row['bot_export_quantity_index']:.4f} | {row['bot_import_quantity_index']:.4f} |\n")
            
        # Write annual table
        f.write("\n## 🗓️ Annual Projections (Volume-Weighted)\n\n")
        f.write("| Year | Export Price Index | Import Price Index | Export Value | Import Value | Export Quantity | Import Quantity |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        fc_a = df_a.loc["2026-12-31":]
        for idx, row in fc_a.iterrows():
            f.write(f"| {idx.year} | {row['bot_export_price_index']:.4f} | {row['bot_import_price_index']:.4f} | {row['bot_export_value_index']:.4f} | {row['bot_import_value_index']:.4f} | {row['bot_export_quantity_index']:.4f} | {row['bot_import_quantity_index']:.4f} |\n")
            
    print("Summary written successfully.")
    
    # Register in central registry
    print("\nRegistering models and visualizations in central registry...")
    try:
        add_model(
            name="Quarterly Resampled Price Indices",
            model_type="Volume-Weighted Aggregation (Quarterly)",
            source_data="export_import_forecast_statsforecast.csv",
            summary_path=summary_path,
            status="Deployed",
            last_update=datetime.now().strftime('%Y-%m-%d')
        )
        add_model(
            name="Annual Resampled Price Indices",
            model_type="Volume-Weighted Aggregation (Annual)",
            source_data="export_import_forecast_statsforecast.csv",
            summary_path=summary_path,
            status="Deployed",
            last_update=datetime.now().strftime('%Y-%m-%d')
        )
        add_visualization(
            name="BOT Official Price Indices Frequency Aggregations",
            chart_type="Line Grid (Multi-frequency)",
            source_data="output/data/forecast/export_import_forecast_quarterly.csv",
            png_path=chart_path,
            status="Rendered",
            last_update=datetime.now().strftime('%Y-%m-%d')
        )
        print("Registration successful.")
    except Exception as e:
        print(f"Error registering: {e}")

if __name__ == "__main__":
    main()

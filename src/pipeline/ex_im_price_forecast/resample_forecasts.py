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
from src.utils.registry import add_model, add_visualization, add_report

# Setup styling
configure_matplotlib_font('FC Vision')
plt.rcParams['figure.facecolor'] = '#FFFFFF'
plt.rcParams['axes.facecolor'] = '#FFFFFF'
plt.rcParams['grid.color'] = '#E9ECEF'
plt.rcParams['grid.alpha'] = 0.7

def main():
    print("Loading datasets...")
    # Load historical wide monthly dataset
    df_wide = pd.read_csv("output/data/ex_im_price_forecast/export_import_price_monthly_wide.csv", index_col=0, parse_dates=True).sort_index()
    
    # Load forecasted monthly dataset
    forecast_path = "output/data/ex_im_price_forecast/export_import_price_forecast_statsforecast.csv"
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
            
    # Generate Quantity forecasts directly using Auto-ARIMA (Quantity-First Approach)
    print("\nGenerating Quantity forecasts dynamically using Auto-ARIMA...")
    import pmdarima as pm
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    
    # Fit and forecast export quantity index
    print("Fitting Auto-ARIMA for bot_export_quantity_index...")
    qty_ex_hist = df_wide["bot_export_quantity_index"].dropna()
    model_ex = pm.auto_arima(qty_ex_hist, seasonal=True, m=12, d=1, D=1, trace=False, error_action='ignore', suppress_warnings=True)
    ex_qty_fit = SARIMAX(qty_ex_hist, order=model_ex.order, seasonal_order=model_ex.seasonal_order).fit(disp=False)
    fc_ex_qty = ex_qty_fit.forecast(steps=len(df_fc))
    
    # Fit and forecast import quantity index
    print("Fitting Auto-ARIMA for bot_import_quantity_index...")
    qty_im_hist = df_wide["bot_import_quantity_index"].dropna()
    model_im = pm.auto_arima(qty_im_hist, seasonal=True, m=12, d=1, D=1, trace=False, error_action='ignore', suppress_warnings=True)
    im_qty_fit = SARIMAX(qty_im_hist, order=model_im.order, seasonal_order=model_im.seasonal_order).fit(disp=False)
    fc_im_qty = im_qty_fit.forecast(steps=len(df_fc))
    
    df_fc["bot_export_quantity_index"] = fc_ex_qty.values
    df_fc["bot_import_quantity_index"] = fc_im_qty.values
    
    # Compute implied value indices: V = (P * Q) / 100
    df_fc["bot_export_value_index"] = (df_fc["bot_export_price_index"] * df_fc["bot_export_quantity_index"]) / 100.0
    df_fc["bot_import_value_index"] = (df_fc["bot_import_price_index"] * df_fc["bot_import_quantity_index"]) / 100.0
    
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
    q_out_path = "output/data/ex_im_price_forecast/export_import_price_forecast_quarterly.csv"
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
    a_out_path = "output/data/ex_im_price_forecast/export_import_price_forecast_annual.csv"
    df_a.to_csv(a_out_path)
    print(f"Saved annual aggregated dataset to {a_out_path} (Shape: {df_a.shape})")
    
    # Calculate YoY growths
    df_q["bot_export_price_index_yoy"] = df_q["bot_export_price_index"].pct_change(4) * 100
    df_q["bot_import_price_index_yoy"] = df_q["bot_import_price_index"].pct_change(4) * 100
    df_a["bot_export_price_index_yoy"] = df_a["bot_export_price_index"].pct_change(1) * 100
    df_a["bot_import_price_index_yoy"] = df_a["bot_import_price_index"].pct_change(1) * 100

    # ------------------ 3. Plot Aggregations (YoY Growth Charts) ------------------
    print("\nPlotting YoY growth aggregations...")
    
    # 3a. Plot Quarterly YoY (2026Q1 to 2027Q4)
    q_subset = df_q.loc["2026-03-31":"2027-12-31"]
    q_labels = [f"{idx.year}Q{idx.quarter}" for idx in q_subset.index]
    x_q = np.arange(len(q_labels))
    width = 0.35
    
    fig_q, ax_q = plt.subplots(figsize=(10, 6))
    rects_q1 = ax_q.bar(x_q - width/2, q_subset["bot_export_price_index_yoy"], width, label="Export Price YoY (%)", color="#1E3A8A")
    rects_q2 = ax_q.bar(x_q + width/2, q_subset["bot_import_price_index_yoy"], width, label="Import Price YoY (%)", color="#FFA300")
    
    ax_q.set_title("Quarterly Price Index YoY Growth Forecast (2026Q1 - 2027Q4)", fontsize=13, fontweight="bold", pad=15)
    ax_q.set_ylabel("YoY Growth Rate (%)", fontsize=11)
    ax_q.set_xticks(x_q)
    ax_q.set_xticklabels(q_labels)
    ax_q.axhline(0, color='black', linewidth=0.8, alpha=0.7)
    ax_q.grid(True, alpha=0.3, axis="y")
    ax_q.legend(loc="upper right", frameon=True, fontsize=10)
    
    def autolabel(ax, rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f"{height:.2f}%",
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3 if height >= 0 else -12),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8.5, fontweight="semibold")
                        
    autolabel(ax_q, rects_q1)
    autolabel(ax_q, rects_q2)
    
    plt.tight_layout()
    q_chart_path = "output/chart/ex_im_price_forecast/export_import_price_forecast_quarterly_yoy.png"
    plt.savefig(q_chart_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved quarterly YoY forecast chart to {q_chart_path}")
    
    # 3b. Plot Annual YoY (2020 to 2027)
    a_subset = df_a.loc["2020-12-31":"2027-12-31"]
    a_labels = [str(idx.year) for idx in a_subset.index]
    x_a = np.arange(len(a_labels))
    
    fig_a, ax_a = plt.subplots(figsize=(10, 6))
    rects_a1 = ax_a.bar(x_a - width/2, a_subset["bot_export_price_index_yoy"], width, label="Export Price YoY (%)", color="#1E3A8A")
    rects_a2 = ax_a.bar(x_a + width/2, a_subset["bot_import_price_index_yoy"], width, label="Import Price YoY (%)", color="#FFA300")
    
    ax_a.set_title("Annual Price Index YoY Growth (2020 - 2027)", fontsize=13, fontweight="bold", pad=15)
    ax_a.set_ylabel("YoY Growth Rate (%)", fontsize=11)
    ax_a.set_xticks(x_a)
    ax_a.set_xticklabels(a_labels)
    ax_a.axhline(0, color='black', linewidth=0.8, alpha=0.7)
    ax_a.grid(True, alpha=0.3, axis="y")
    ax_a.legend(loc="upper left", frameon=True, fontsize=10)
    
    autolabel(ax_a, rects_a1)
    autolabel(ax_a, rects_a2)
    
    plt.tight_layout()
    a_chart_path = "output/chart/ex_im_price_forecast/export_import_price_forecast_annual_yoy.png"
    plt.savefig(a_chart_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved annual YoY forecast chart to {a_chart_path}")

    # ------------------ 4. Plot Quantity Index Forecasts ------------------
    print("\nPlotting Quantity Index forecasts...")
    fig_qty, axes_qty = plt.subplots(1, 2, figsize=(16, 6))
    plot_start_date = "2000-01-01"
    hist_subset = df_wide.loc[plot_start_date:]
    
    # Export Quantity Plot
    ax = axes_qty[0]
    ax.plot(hist_subset.index, hist_subset["bot_export_quantity_index"], label="Historical Export Quantity Index", color="#2B2D42", linewidth=2)
    ax.plot(df_fc.index, df_fc["bot_export_quantity_index"], label="Forecast Export Quantity Index (Projected)", color="#00109E", linewidth=2.5, linestyle="--")
    ax.axvline(pd.to_datetime("2026-04-01"), color="red", linestyle=":", label="Forecast Start (May 2026)", alpha=0.8)
    ax.set_title("Export Quantity Index Projections", fontsize=13, fontweight="bold", pad=12)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper left", frameon=True, fontsize=10)
    
    # Import Quantity Plot
    ax = axes_qty[1]
    ax.plot(hist_subset.index, hist_subset["bot_import_quantity_index"], label="Historical Import Quantity Index", color="#2B2D42", linewidth=2)
    ax.plot(df_fc.index, df_fc["bot_import_quantity_index"], label="Forecast Import Quantity Index (Projected)", color="#FFA300", linewidth=2.5, linestyle="--")
    ax.axvline(pd.to_datetime("2026-04-01"), color="red", linestyle=":", label="Forecast Start (May 2026)", alpha=0.8)
    ax.set_title("Import Quantity Index Projections", fontsize=13, fontweight="bold", pad=12)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper left", frameon=True, fontsize=10)
    
    plt.tight_layout()
    qty_chart_path = "output/chart/ex_im_price_forecast/export_import_price_forecast_quantities.png"
    plt.savefig(qty_chart_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved quantity forecast chart to {qty_chart_path}")
    
    # Write a small summary file
    summary_path = "output/model_summary/ex_im_price_forecast/export_import_price_forecast_resampled_summary.txt"
    print(f"Writing summary to {summary_path}...")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# BOT Official Price Indices: Quarterly & Annual Aggregations (YoY Growth Edition)\n\n")
        f.write("This document details the volume-weighted resampling and YoY growth rate calculations for Export and Import Price Indices.\n\n")
        f.write("## 📅 Quarterly Projections & YoY Growth\n\n")
        f.write("| Quarter | Export Price Index | Import Price Index | Export YoY Growth | Import YoY Growth |\n")
        f.write("|---|---|---|---|---|\n")
        for idx, row in q_subset.iterrows():
            q_name = f"{idx.year}Q{idx.quarter}"
            f.write(f"| {q_name} | {row['bot_export_price_index']:.4f} | {row['bot_import_price_index']:.4f} | {row['bot_export_price_index_yoy']:.2f}% | {row['bot_import_price_index_yoy']:.2f}% |\n")
            
        f.write("\n## 🗓️ Annual Projections & YoY Growth\n\n")
        f.write("| Year | Export Price Index | Import Price Index | Export YoY Growth | Import YoY Growth |\n")
        f.write("|---|---|---|---|---|\n")
        for idx, row in a_subset.iterrows():
            f.write(f"| {idx.year} | {row['bot_export_price_index']:.4f} | {row['bot_import_price_index']:.4f} | {row['bot_export_price_index_yoy']:.2f}% | {row['bot_import_price_index_yoy']:.2f}% |\n")
            
    print("Summary written successfully.")
    
    # ------------------ 5. Update Markdown Report ------------------
    report_path = "report/ex_im_price_forecast/ex_im_price_forecast.md"
    if os.path.exists(report_path):
        print(f"Updating report at {report_path}...")
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
            
        start_marker = "### Quarterly Volume-Weighted Projections"
        end_marker = "## 4. Policy & Strategic Implications"
        
        start_idx = report_content.find(start_marker)
        end_idx = report_content.find(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            new_section_content = []
            new_section_content.append("### Quarterly Volume-Weighted Projections")
            new_section_content.append("In national accounting, arithmetic averages fail to capture variations in monthly trade volumes. We apply standard **Volume-Weighted Resampling** to calculate the quarterly indicators.\n")
            new_section_content.append("The table below presents the quarterly price index projections and their corresponding Year-on-Year (YoY) growth rates from Q1-2026 to Q4-2027:\n")
            
            new_section_content.append("| Quarter | Export Price Index | Import Price Index | Export YoY Growth (%) | Import YoY Growth (%) | Export Quantity | Import Quantity |")
            new_section_content.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
            for idx, row in q_subset.iterrows():
                q_name = f"**{idx.year}Q{idx.quarter}**"
                new_section_content.append(f"| {q_name} | {row['bot_export_price_index']:.4f} | {row['bot_import_price_index']:.4f} | {row['bot_export_price_index_yoy']:.2f}% | {row['bot_import_price_index_yoy']:.2f}% | {row['bot_export_quantity_index']:.4f} | {row['bot_import_quantity_index']:.4f} |")
            
            new_section_content.append("\n*Note: YoY growth rate for quarter t is computed relative to quarter t-4 (the same quarter in the previous year).*\n")
            new_section_content.append("![Quarterly YoY Price Index Growth Forecast](../../output/chart/ex_im_price_forecast/export_import_price_forecast_quarterly_yoy.png)\n")
            
            new_section_content.append("### Annual Forecast & YoY Growth (2020–2027)")
            new_section_content.append("The table below displays the annual resampled indicators from 2020 to 2027 along with their Year-on-Year (YoY) growth rates:\n")
            
            new_section_content.append("| Year | Export Price Index | Import Price Index | Export YoY Growth (%) | Import YoY Growth (%) | Export Quantity | Import Quantity |")
            new_section_content.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
            for idx, row in a_subset.iterrows():
                y_name = f"**{idx.year}**"
                new_section_content.append(f"| {y_name} | {row['bot_export_price_index']:.4f} | {row['bot_import_price_index']:.4f} | {row['bot_export_price_index_yoy']:.2f}% | {row['bot_import_price_index_yoy']:.2f}% | {row['bot_export_quantity_index']:.4f} | {row['bot_import_quantity_index']:.4f} |")
                
            new_section_content.append("\n*Note: YoY growth rate for year t is computed relative to year t-1.*\n")
            new_section_content.append("![Annual YoY Price Index Growth Forecast](../../output/chart/ex_im_price_forecast/export_import_price_forecast_annual_yoy.png)\n")
            new_section_content.append("---\n\n")
            
            replacement_str = "\n".join(new_section_content)
            updated_report_content = report_content[:start_idx] + replacement_str + report_content[end_idx:]
            
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(updated_report_content)
            print("Successfully updated report with quarterly and annual YoY sections!")
        else:
            print("Error: Could not find start or end marker in report.")

    # Register in central registry
    print("\nRegistering models and visualizations in central registry...")
    try:
        add_model(
            name="Quarterly Resampled Price Indices",
            model_type="Volume-Weighted Aggregation (Quarterly)",
            source_data="export_import_price_forecast_statsforecast.csv",
            summary_path=summary_path,
            status="Deployed",
            last_update=datetime.now().strftime('%Y-%m-%d')
        )
        add_model(
            name="Annual Resampled Price Indices",
            model_type="Volume-Weighted Aggregation (Annual)",
            source_data="export_import_price_forecast_statsforecast.csv",
            summary_path=summary_path,
            status="Deployed",
            last_update=datetime.now().strftime('%Y-%m-%d')
        )
        add_visualization(
            name="BOT Official Price Indices Quarterly YoY Growth",
            chart_type="Bar Chart (Quarterly)",
            source_data="output/data/ex_im_price_forecast/export_import_price_forecast_quarterly.csv",
            png_path=q_chart_path,
            status="Rendered",
            last_update=datetime.now().strftime('%Y-%m-%d')
        )
        add_visualization(
            name="BOT Official Price Indices Annual YoY Growth",
            chart_type="Bar Chart (Annual)",
            source_data="output/data/ex_im_price_forecast/export_import_price_forecast_annual.csv",
            png_path=a_chart_path,
            status="Rendered",
            last_update=datetime.now().strftime('%Y-%m-%d')
        )
        add_visualization(
            name="BOT Quantity Indices Projections",
            chart_type="Line Grid (Quantity)",
            source_data=forecast_path,
            png_path=qty_chart_path,
            status="Rendered",
            last_update=datetime.now().strftime('%Y-%m-%d')
        )
        add_report(
            title="Export & Import Price Forecast Report",
            author="Chief Economist",
            path="report/ex_im_price_forecast/ex_im_price_forecast.md",
            status="Published"
        )
        print("Registration successful.")
    except Exception as e:
        print(f"Error registering: {e}")

if __name__ == "__main__":
    main()

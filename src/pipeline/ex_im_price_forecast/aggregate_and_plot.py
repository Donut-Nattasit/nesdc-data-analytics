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

# Setup styling
configure_matplotlib_font('FC Vision')
plt.rcParams['figure.facecolor'] = '#FFFFFF'
plt.rcParams['axes.facecolor'] = '#FFFFFF'
plt.rcParams['grid.color'] = '#E9ECEF'
plt.rcParams['grid.alpha'] = 0.7

def main():
    print("Loading datasets...")
    # Load historical wide dataset
    df_wide = pd.read_csv("output/data/ex_im_price_forecast/export_import_price_monthly_wide.csv", index_col=0, parse_dates=True).sort_index()
    
    # Load forecasted components dataset
    forecast_path = "output/data/ex_im_price_forecast/export_import_price_forecast_statsforecast.csv"
    if not os.path.exists(forecast_path):
        print(f"Error: {forecast_path} not found. Please run the forecasting scripts first.")
        raise RuntimeError("Pipeline step failed")
        
    df_fc = pd.read_csv(forecast_path, index_col=0, parse_dates=True).sort_index()
    
    # Define components
    export_comps = ["ceic_expi_agro_industrial", "ceic_expi_agricultural", "ceic_expi_mineral_fuel", "ceic_expi_principal_manuf"]
    import_comps = ["ceic_impi_capital_goods", "ceic_impi_consumer_goods", "ceic_impi_fuel", "ceic_impi_raw_materials", "ceic_impi_vehicle_equip"]
    
    export_wgts = ["wgt_expi_agro_industrial", "wgt_expi_agricultural", "wgt_expi_mineral_fuel", "wgt_expi_principal_manuf"]
    import_wgts = ["wgt_impi_capital_goods", "wgt_impi_consumer_goods", "wgt_impi_fuel", "wgt_impi_raw_materials", "wgt_impi_vehicle_equip"]
    
    # 1. Retrieve latest known weights (from 2026-04-01)
    latest_date = df_wide[[f"wgt_expi_{c.replace('ceic_expi_', '')}" for c in export_comps]].dropna().index[-1]
    print(f"Using weights from latest actual date: {latest_date.strftime('%Y-%m-%d')}")
    
    wgts_ex = {c: df_wide.loc[latest_date, f"wgt_expi_{c.replace('ceic_expi_', '')}"] for c in export_comps}
    wgts_im = {c: df_wide.loc[latest_date, f"wgt_impi_{c.replace('ceic_impi_', '')}"] for c in import_comps}
    
    print("\nExport weights:")
    for c, w in wgts_ex.items():
        print(f"  {c}: {w:.4f}%")
        
    print("\nImport weights:")
    for c, w in wgts_im.items():
        print(f"  {c}: {w:.4f}%")
        
    # 2. Calculate raw composite forecasts
    print("\nCalculating raw weighted composites...")
    fc_composite_ex_raw = sum(df_fc[c] * (wgts_ex[c] / 100.0) for c in export_comps)
    fc_composite_im_raw = sum(df_fc[c] * (wgts_im[c] / 100.0) for c in import_comps)
    
    # 3. Calculate level-adjusted (spliced) composite forecasts
    # Find overlapping actual composite values on latest actual date
    actual_comp_ex = df_wide.loc[latest_date, "ceic_expi_composite"]
    actual_comp_im = df_wide.loc[latest_date, "ceic_impi_composite"]
    
    # Calculate historical weighted average at that same date for ratio calibration
    hist_comp_ex_raw = sum(df_wide.loc[latest_date, c] * (wgts_ex[c] / 100.0) for c in export_comps)
    hist_comp_im_raw = sum(df_wide.loc[latest_date, c] * (wgts_im[c] / 100.0) for c in import_comps)
    
    ratio_ex = actual_comp_ex / hist_comp_ex_raw
    ratio_im = actual_comp_im / hist_comp_im_raw
    
    print(f"\nLevel adjustment splice factors:")
    print(f"  Export: Actual {actual_comp_ex:.4f} / Weighted Raw {hist_comp_ex_raw:.4f} = Ratio {ratio_ex:.6f}")
    print(f"  Import: Actual {actual_comp_im:.4f} / Weighted Raw {hist_comp_im_raw:.4f} = Ratio {ratio_im:.6f}")
    
    fc_composite_ex_adj = fc_composite_ex_raw * ratio_ex
    fc_composite_im_adj = fc_composite_im_raw * ratio_im
    
    # 3b. Project BOT Price Indices using growth rates of the spliced composite forecasts
    actual_bot_ex = df_wide.loc[latest_date, "bot_export_price_index"]
    actual_bot_im = df_wide.loc[latest_date, "bot_import_price_index"]
    
    print(f"\nProjecting BOT Price Indices (spliced growth rate method):")
    print(f"  Export: Latest BOT Actual = {actual_bot_ex:.4f}")
    print(f"  Import: Latest BOT Actual = {actual_bot_im:.4f}")
    
    fc_bot_ex = actual_bot_ex * (fc_composite_ex_adj / actual_comp_ex)
    fc_bot_im = actual_bot_im * (fc_composite_im_adj / actual_comp_im)
    
    # Add to forecast dataframe
    df_fc["ceic_expi_composite_raw"] = fc_composite_ex_raw
    df_fc["ceic_impi_composite_raw"] = fc_composite_im_raw
    df_fc["ceic_expi_composite"] = fc_composite_ex_adj
    df_fc["ceic_impi_composite"] = fc_composite_im_adj
    df_fc["bot_export_price_index"] = fc_bot_ex
    df_fc["bot_import_price_index"] = fc_bot_im
    
    # Save back to CSV
    df_fc.to_csv(forecast_path)
    print(f"\nUpdated forecast CSV with composites and BOT indices: {forecast_path}")
    
    # 4. Plot composite indices (Historical + Forecast)
    print("\nPlotting BOT official price indices...")
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    plot_start_date = "2000-01-01"
    hist_subset = df_wide.loc[plot_start_date:]
    
    # Export Price Index Subplot (BOT Official)
    ax = axes[0]
    ax.plot(hist_subset.index, hist_subset["bot_export_price_index"], label="Historical BOT Export Price Index", color="#2B2D42", linewidth=2)
    ax.plot(df_fc.index, df_fc["bot_export_price_index"], label="Forecast BOT Export Price Index (Projected)", color="#00109E", linewidth=2.5, linestyle="--")
    ax.axvline(pd.to_datetime("2026-04-01"), color="red", linestyle=":", label="Forecast Start (May 2026)", alpha=0.8)
    
    ax.set_title("Export Price Index: Official BOT Series", fontsize=13, fontweight="bold", pad=12)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper left", frameon=True, fontsize=10)
    
    # Import Price Index Subplot (BOT Official)
    ax = axes[1]
    ax.plot(hist_subset.index, hist_subset["bot_import_price_index"], label="Historical BOT Import Price Index", color="#2B2D42", linewidth=2)
    ax.plot(df_fc.index, df_fc["bot_import_price_index"], label="Forecast BOT Import Price Index (Projected)", color="#FFA300", linewidth=2.5, linestyle="--")
    ax.axvline(pd.to_datetime("2026-04-01"), color="red", linestyle=":", label="Forecast Start (May 2026)", alpha=0.8)
    
    ax.set_title("Import Price Index: Official BOT Series", fontsize=13, fontweight="bold", pad=12)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper left", frameon=True, fontsize=10)
    
    plt.tight_layout()
    chart_path = "output/chart/ex_im_price_forecast/export_import_price_forecast_composites.png"
    plt.savefig(chart_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved BOT composites forecast chart to {chart_path}")
    
    # Write a small summary file
    summary_path = "output/model_summary/ex_im_price_forecast/export_import_price_forecast_composite_summary.txt"
    print(f"Writing summary to {summary_path}...")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# Export & Import Composite Price Indices Aggregation\n\n")
        f.write("This document details the aggregation of forecasted price component indices into their respective composite Export and Import Price Indices, projected on the official BOT series.\n\n")
        f.write("## ⚖️ Weighting Scheme (Naive Method)\n")
        f.write(f"The future weights are assumed to remain constant at the latest known historical data point (**{latest_date.strftime('%Y-%m-%d')}**):\n\n")
        
        f.write("### 🚢 Export Weights\n")
        for c, w in wgts_ex.items():
            f.write(f"- **{c.replace('ceic_expi_', '').replace('_', ' ').title()}**: {w:.4f}%\n")
            
        f.write("\n### 📥 Import Weights\n")
        for c, w in wgts_im.items():
            f.write(f"- **{c.replace('ceic_impi_', '').replace('_', ' ').title()}**: {w:.4f}%\n")
            
        f.write("\n## 🔗 Aggregation & Splicing Methodology\n")
        f.write("Direct raw weighted average aggregation creates level shifts due to chain-weighting discrepancy in historical index series published by the Ministry of Commerce. To preserve level continuity, we apply a splicing ratio factor defined as:\n\n")
        f.write("$$\\text{Ratio} = \\frac{\\text{Actual Composite Index at Overlap}}{\\text{Raw Weighted Average Index at Overlap}}$$\n\n")
        f.write(f"- **Export Splicing Ratio**: `{ratio_ex:.6f}` (Actual {actual_comp_ex:.2f} vs. Weighted {hist_comp_ex_raw:.2f})\n")
        f.write(f"- **Import Splicing Ratio**: `{ratio_im:.6f}` (Actual {actual_comp_im:.2f} vs. Weighted {hist_comp_im_raw:.2f})\n\n")
        
        f.write("## 🏦 BOT Official Price Indices Forecast (Growth Spliced)\n")
        f.write("Projected by applying the growth rate of the spliced CEIC composite index to the latest actual BOT value on April 2026:\n\n")
        f.write("| Month | BOT Export Price Index Forecast | BOT Import Price Index Forecast |\n")
        f.write("|---|---|---|\n")
        for idx, row in df_fc.iterrows():
            f.write(f"| {idx.strftime('%Y-%m-%d')} | {row['bot_export_price_index']:.4f} | {row['bot_import_price_index']:.4f} |\n")
            
    print("Summary written successfully.")
    
    try:
    except Exception as e:

if __name__ == "__main__":
    main()

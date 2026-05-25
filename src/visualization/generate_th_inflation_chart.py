import os
import sys
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to sys.path programmatically
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.api.imf_client import IMFClient
from src.visualization.charts import configure_matplotlib_font

def generate_thailand_inflation_analysis():
    print("==================================================")
    print("   THAILAND INFLATION RETRIEVAL & VISUALIZATION   ")
    print("==================================================")
    
    # 1. Initialize Client and Fetch Data
    client = IMFClient()
    indicator = "PCPIPCH"  # Inflation, average consumer prices (Annual percent change)
    country = "THA"        # Thailand country code
    
    print(f"[Phase 1] Querying live IMF WEO SDMX 3.0 API for Thailand ({country})...")
    df_tidy = client.get_weo_data(
        country=country,
        indicator=indicator,
        start_period="2015",
        end_period="2031",
        force_refresh=True
    )
    
    if df_tidy.empty:
        print("[FAIL] Failed to retrieve data from IMF API.")
        return
        
    print(f"Successfully retrieved {len(df_tidy)} observations.")
    
    # Clean and filter dates to strictly 2015-2031 range as requested
    def extract_year_str(d_str):
        return str(d_str).split("-")[0]
        
    df_tidy["date"] = df_tidy["date"].apply(extract_year_str)
    
    # Filter only 2015 to 2031
    df_tidy["year_int"] = df_tidy["date"].astype(int)
    df_tidy = df_tidy[(df_tidy["year_int"] >= 2015) & (df_tidy["year_int"] <= 2031)]
    df_tidy = df_tidy.drop(columns=["year_int"])
    
    # Sort by date for logical time series flow
    df_tidy = df_tidy.sort_values(by="date")
    
    # Rename series representation for wide format column
    df_tidy["Series"] = "Thailand"
    
    # 2. Pivot to Wide Format
    print("[Phase 2] Pivoting data to wide format...")
    df_wide = df_tidy.pivot(index="date", columns="Series", values="value")
    df_wide.index.name = "date"
    
    print("\nProcessed Wide Format Dataset:")
    print(df_wide)
    print()
    
    # 3. Store Data
    print("[Phase 3] Storing datasets...")
    # Save CSV
    os.makedirs("output/data", exist_ok=True)
    csv_path = "output/data/thailand_inflation.csv"
    df_wide.to_csv(csv_path)
    print(f"  -> Saved CSV to: {csv_path}")
    
    # Save to SQLite database
    db_path = "database/time_series.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        df_wide.to_sql("thailand_inflation", conn, if_exists="replace", index=True)
        conn.commit()
        print(f"  -> Saved table 'thailand_inflation' to SQLite database: {db_path}")
    except Exception as e:
        print(f"[Warning] Failed to write to SQLite database: {e}")
    finally:
        conn.close()
        
    # 4. Generate Premium Visualization
    print("[Phase 4] Designing and rendering premium line chart...")
    configure_matplotlib_font('FC Vision')
    
    # Setup styling parameters
    plt.rcParams['figure.facecolor'] = '#FFFFFF'  # Pure white background
    plt.rcParams['axes.facecolor'] = '#FFFFFF'
    plt.rcParams['grid.color'] = '#E9ECEF'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.linewidth'] = 0.8
    
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    
    # Plot line and markers
    x_years = df_wide.index.tolist()
    y_values = df_wide["Thailand"].tolist()
    
    # Official NESDC Solid Color Palette Integration
    line_color = "#00109E"       # Sapphire Blue (Primary 60%)
    marker_color = "#60B1E7"     # Maya Blue (Secondary 5%)
    forecast_border = "#FFA300"  # Saffron Accent
    
    ax.plot(x_years, y_values, color=line_color, linewidth=2.8, marker='o', markersize=7, 
            markerfacecolor=marker_color, markeredgecolor='#FFFFFF', markeredgewidth=1.5,
            label="Thailand Inflation Rate (Average Consumer Prices, YoY %)")
    
    # Shaded Forecast Horizon: WEO April 2026 indicates 2026-2031 are forecasts
    # 2015-2025 are historical.
    forecast_start_idx = x_years.index("2026")
    ax.axvspan(forecast_start_idx - 0.5, len(x_years) - 0.5, color='#E8F4FC', alpha=0.8, 
               label="Forecast Horizon (WEO April 2026)")
    ax.axvline(x=forecast_start_idx - 0.5, color=forecast_border, linestyle="--", linewidth=1.5)
    
    # Text label for forecast boundary
    ax.text(forecast_start_idx - 0.4, max(y_values) - 0.5, "WEO Forecast Horizon ->", 
            color=forecast_border, fontsize=10, fontweight="bold", fontstyle="italic")
    
    # Zero baseline guide
    ax.axhline(0, color='#8D99AE', linestyle='-', linewidth=1.0)
    
    # Annotations for key landmarks
    # 1. COVID-19 Dip: 2020 (-0.85%)
    idx_2020 = x_years.index("2020")
    val_2020 = y_values[idx_2020]
    ax.annotate(f"COVID-19 Shock\n2020: {val_2020:.2f}%", 
                xy=(idx_2020, val_2020), 
                xytext=(idx_2020 - 1.8, val_2020 - 1.2),
                arrowprops=dict(facecolor=forecast_border, shrink=0.08, width=1, headwidth=6, headlength=6),
                fontsize=10.5, fontweight='semibold', color='#C27C00',
                bbox=dict(boxstyle='round,pad=0.3', fc='#FFF9E6', ec=forecast_border, alpha=0.9))
                
    # 2. Rebound & Energy Shock Peak: 2022 (6.08%)
    idx_2022 = x_years.index("2022")
    val_2022 = y_values[idx_2022]
    ax.annotate(f"Global Energy & Supply Shock\n2022: {val_2022:.2f}%", 
                xy=(idx_2022, val_2022), 
                xytext=(idx_2022 - 2.8, val_2022 - 1.2),
                arrowprops=dict(facecolor='#FF4D4F', shrink=0.08, width=1, headwidth=6, headlength=6),
                fontsize=10.5, fontweight='semibold', color='#C41D7F',
                bbox=dict(boxstyle='round,pad=0.3', fc='#FFF0F6', ec='#FF4D4F', alpha=0.9))
                
    # 3. 2026 Forecast: (0.92%)
    idx_2026 = x_years.index("2026")
    val_2026 = y_values[idx_2026]
    ax.annotate(f"WEO April 2026 Forecast\n2026: {val_2026:.2f}%", 
                xy=(idx_2026, val_2026), 
                xytext=(idx_2026 + 0.6, val_2026 + 1.2),
                arrowprops=dict(facecolor=line_color, shrink=0.08, width=1, headwidth=6, headlength=6),
                fontsize=10.5, fontweight='semibold', color=line_color,
                bbox=dict(boxstyle='round,pad=0.3', fc='#E6E8F7', ec=line_color, alpha=0.9))

    # Add numeric labels to all forecast points for clarity (excluding 2026 which has custom annotation)
    for idx in range(forecast_start_idx, len(x_years)):
        yr = x_years[idx]
        val = y_values[idx]
        if yr != "2026":
            ax.text(idx, val + 0.25, f"{val:.1f}%", ha='center', fontsize=9, color="#1D3557", fontweight="bold")
            
    # Chart styling details
    ax.set_title("Thailand Consumer Price Inflation & Medium-Term Outlook", fontsize=18, fontweight='bold', color='#1D3557', pad=25)
    ax.set_xlabel(None)
    ax.xaxis.label.set_visible(False)
    ax.set_ylabel("Average Consumer Prices (Annual % Change)", fontsize=12, fontweight='semibold', color='#1D3557', labelpad=12)
    
    # Limits and grid tuning
    ax.set_ylim(-2.5, 7.5)
    ax.grid(True, which='major', axis='both')
    
    # Legend - positioned underneath the chart
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.06),
        ncol=2,
        frameon=True,
        facecolor="#FFFFFF",
        edgecolor="#E9ECEF",
        framealpha=0.9,
        fontsize=10.5
    )
    
    # Source caption at the absolute bottom
    plt.figtext(0.1, 0.01, 
                "Source: IMF World Economic Outlook (WEO) April 2026 Database. Projections cover 2026–2031.\nDisclaimer: Developed under Chief Economist direction in wide-format SQLite standard.",
                fontsize=9, color='#8D99AE', fontstyle='italic')
    
    plt.tight_layout()
    # Explicitly allocate bottom margin for a tight layout snug with the legend
    fig.subplots_adjust(bottom=0.14)
    
    chart_path = "output/chart/thailand_inflation_weo.png"
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    plt.savefig(chart_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    
    print(f"Successfully generated and saved line chart to: {chart_path}")
    print("==================================================")

if __name__ == "__main__":
    generate_thailand_inflation_analysis()

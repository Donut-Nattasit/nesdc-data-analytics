import os
import sys
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# Load environmental variables from .env
load_dotenv()

# Add project root to sys.path programmatically
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.api.imf_client import IMFClient
from src.visualization.charts import configure_matplotlib_font

def generate_asean_gdp_analysis():
    print("==================================================")
    print("      ASEAN GDP RETRIEVAL & VISUALIZATION         ")
    print("==================================================")
    
    # 1. Initialize Client and Fetch Data
    client = IMFClient()
    countries = "IDN+PHL+MYS+THA"
    indicator = "NGDP_RPCH"  # Real GDP Growth (Annual percent change)
    
    print(f"[Phase 1] Querying live IMF WEO SDMX 3.0 API for: {countries}...")
    df_tidy = client.get_weo_data(
        country=countries,
        indicator=indicator,
        start_period="2018",
        end_period="2031"
    )
    
    if df_tidy.empty:
        print("[FAIL] Failed to retrieve data from IMF API.")
        return
        
    print(f"Successfully retrieved {len(df_tidy)} tidy observations.")
    
    # Clean and filter dates to strictly 2018-2031 range as requested
    def extract_year_str(d_str):
        return str(d_str).split("-")[0]
        
    df_tidy["date"] = df_tidy["date"].apply(extract_year_str)
    
    # Filter only 2018 to 2031
    df_tidy["year_int"] = df_tidy["date"].astype(int)
    df_tidy = df_tidy[(df_tidy["year_int"] >= 2018) & (df_tidy["year_int"] <= 2031)]
    df_tidy = df_tidy.drop(columns=["year_int"])
    
    # Sort by date for logical time series flow
    df_tidy = df_tidy.sort_values(by=["COUNTRY", "date"])
    
    # 2. Pivot to Wide Format
    print("[Phase 2] Pivoting data to wide format...")
    df_wide = df_tidy.pivot(index="date", columns="COUNTRY", values="value")
    df_wide.index.name = "date"
    
    # Check that we got all 4 countries
    expected_cols = ["IDN", "MYS", "PHL", "THA"]
    actual_cols = sorted(df_wide.columns.tolist())
    print(f"Wide Format Columns: {actual_cols}")
    
    # 3. Store Data
    print("[Phase 3] Storing datasets...")
    # Save CSV
    os.makedirs("output/data", exist_ok=True)
    csv_path = "output/data/asean_gdp_growth.csv"
    df_wide.to_csv(csv_path)
    print(f"  -> Saved CSV to: {csv_path}")
    
    # Save to SQLite database
    db_path = "database/core/time_series.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        df_wide.to_sql("asean_gdp_growth", conn, if_exists="replace", index=True)
        conn.commit()
        print(f"  -> Saved table 'asean_gdp_growth' to SQLite database: {db_path}")
    except Exception as e:
        print(f"[Warning] Failed to write to SQLite database: {e}")
    finally:
        conn.close()
        
    # 4. Generate Premium Visualization
    print("[Phase 4] Designing and rendering premium line chart...")
    # Register and set local FC Vision font if available
    configure_matplotlib_font('FC Vision')
    
    # Setup styling parameters
    plt.rcParams['figure.facecolor'] = '#FFFFFF'  # Pure white background
    plt.rcParams['axes.facecolor'] = '#FFFFFF'
    plt.rcParams['grid.color'] = '#E9ECEF'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.linewidth'] = 0.8
    
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    
    # Official NESDC Solid Color Palette mapping
    colors = {
        "THA": "#00109E",  # Sapphire Blue (Primary 60% - Thailand as main reference)
        "IDN": "#78DED4",  # Caribbean Sea (Secondary 15% - Indonesia)
        "MYS": "#BFB997",  # Clay (Secondary 15% - Malaysia)
        "PHL": "#60B1E7"   # Maya Blue (Secondary 5% - Philippines)
    }

    
    markers = {
        "IDN": "o",  # Circle
        "MYS": "s",  # Square
        "PHL": "D",  # Diamond
        "THA": "^"   # Triangle
    }
    
    country_names = {
        "IDN": "Indonesia",
        "MYS": "Malaysia",
        "PHL": "Philippines",
        "THA": "Thailand"
    }
    
    years = sorted(df_wide.index.tolist())
    
    def get_year_int(y_str):
        return int(str(y_str).split("-")[0])
        
    years_int = [get_year_int(y) for y in years]
    
    # Historical vs. Forecast boundary (WEO April 2026 indicates 2026-2031 are forecasts, 2018-2025 are historical)
    forecast_start_year = 2025  # The transition happens between 2025 and 2026
    
    # Plot each country series
    for country in expected_cols:
        if country not in df_wide.columns:
            continue
            
        series = df_wide[country]
        
        # Segment data into historical (<= 2025) and forecast (>= 2025 to create seamless link)
        hist_years = [y for y in years if get_year_int(y) <= forecast_start_year]
        fore_years = [y for y in years if get_year_int(y) >= forecast_start_year]
        
        hist_values = series.loc[hist_years].tolist()
        fore_values = series.loc[fore_years].tolist()
        
        # Plot Historical solid line
        ax.plot(
            hist_years,
            hist_values,
            color=colors[country],
            linestyle="-",
            linewidth=2.5,
            marker=markers[country],
            markersize=6,
            label=country_names[country]
        )
        
        # Plot Forecast dashed line
        ax.plot(
            fore_years,
            fore_values,
            color=colors[country],
            linestyle="--",
            linewidth=2.0,
            marker=markers[country],
            markerfacecolor="none",  # Hollow markers for forecast
            markersize=6,
            markeredgewidth=1.5
        )
        
    # Find boundary date index and label position safely
    try:
        boundary_idx = next(i for i, y in enumerate(years) if get_year_int(y) == forecast_start_year)
        boundary_x_val = years[boundary_idx]
    except StopIteration:
        boundary_idx = len(years) - 1
        boundary_x_val = years[-1]
        
    # Draw vertical boundary line representing historical vs forecast transition
    ax.axvline(
        x=boundary_x_val,
        color="#6C757D",
        linestyle=":",
        linewidth=1.5,
        alpha=0.8
    )
    
    # Label the forecast line
    ax.text(
        x=boundary_idx + 0.1,
        y=ax.get_ylim()[0] + 0.5,
        s="WEO Forecast Horizon ->",
        color="#6c757d",
        fontsize=10,
        fontweight="bold"
    )
    
    # Formatting Axes and Titles
    ax.set_title("ASEAN-4 Real GDP Growth Rate: Historical & Forecast Spans", fontsize=16, fontweight="bold", pad=20, color="#212529")
    ax.set_xlabel(None)
    ax.xaxis.label.set_visible(False)
    ax.set_ylabel("Real GDP Growth Rate (YoY %)", fontsize=12, fontweight="semibold", labelpad=10, color="#495057")
    
    # Configure Grid and Limits
    ax.grid(True, which="both")
    ax.set_axisbelow(True)
    
    # Remove outer spines for clean appearance
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#CED4DA")
    ax.spines["bottom"].set_color("#CED4DA")
    
    # Legend - bottom centered horizontal orientation
    # Positioned closely under the X-axis ticks (bbox_to_anchor=(0.5, -0.06))
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.06),
        ncol=4,
        frameon=True,
        facecolor="#FFFFFF",
        edgecolor="#E9ECEF",
        fontsize=11
    )
    
    # Add footnote/source at the absolute bottom of the figure
    plt.figtext(
        0.1, 0.01,
        "Source: IMF World Economic Outlook (WEO) April 2026 Database. Values beyond 2025 reflect WEO projections.",
        fontsize=9,
        color="#6C757D",
        style="italic"
    )
    
    # Adjust layout dynamically
    plt.tight_layout()
    # Explicitly allocate 14% bottom margin for a tight layout
    fig.subplots_adjust(bottom=0.14)
    
    # Save Image
    os.makedirs("output/chart", exist_ok=True)
    chart_path = "output/chart/asean_gdp_growth.png"
    plt.savefig(chart_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    
    print(f"  -> Saved line chart to: {chart_path}")
    print("==================================================")
    print("      ANALYSIS PIPELINE COMPLETED SUCCESSFULLY     ")
    print("==================================================")

if __name__ == "__main__":
    generate_asean_gdp_analysis()

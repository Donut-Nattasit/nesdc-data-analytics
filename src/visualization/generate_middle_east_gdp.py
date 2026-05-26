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

from src.api.ceic_client import CeicSession
from src.visualization.charts import configure_matplotlib_font

def main():
    print("==================================================")
    print("   MIDDLE EAST GDP PIPELINE: FETCH & VISUALIZE   ")
    print("==================================================")
    
    # 1. Initialize CEIC Session and Fetch Data
    session = CeicSession()
    if not session.authenticate():
        print("[FAIL] CEIC Authentication failed.")
        sys.exit(1)
        
    # Map Series ID to Country Names
    series_map = {
        "455756487": "Saudi Arabia",
        "414341107": "United Arab Emirates",
        "369746997": "Qatar",
        "400655287": "Kuwait",
        "242791303": "Bahrain",
        "210467002": "Egypt",
        "210509802": "Jordan",
        "355821777": "Iran"
    }
    
    series_ids = list(series_map.keys())
    
    print(f"[Phase 1] Fetching {len(series_ids)} Middle East Real GDP Growth series from CEIC...")
    # Fetch without historical extension to bypass NON_CONTINUOUS_SERIES quirk
    df_raw = session.get_data(series_ids, with_historical_extension=False, count=10000)
    
    if df_raw.empty:
        print("[FAIL] No data retrieved from CEIC API.")
        sys.exit(1)
        
    print(f"Successfully retrieved {len(df_raw)} raw data points.")
    
    # 2. Transform and Align Data to Quarter-End (QE)
    print("[Phase 2] Transforming and aligning series data to Quarter-End ('QE')...")
    
    # Map series_id in raw data to Country Name (cast to string to prevent type mismatches)
    df_raw['series_id'] = df_raw['series_id'].astype(str)
    df_raw['Country'] = df_raw['series_id'].map(series_map)
    
    # Check if there are any missing mappings or data issues
    df_clean = df_raw.dropna(subset=['Country', 'date', 'value'])
    
    # Pivot to Wide Format: Index = date, Columns = Country, Values = value
    df_wide = df_clean.pivot_table(index='date', columns='Country', values='value', aggfunc='mean')
    df_wide.index = pd.to_datetime(df_wide.index)
    
    # Resample to standard Quarter-End ('QE') using Mean to ensure regular dates
    df_aligned = df_wide.resample('QE').mean()
    df_aligned.index.name = 'date'
    
    # Filter for data from 2015 to the latest available data to have a beautiful modern window
    df_aligned = df_aligned.loc['2015-01-01':]
    
    print("\n--- Aligned Wide Format Data (Recent Observations) ---")
    print(df_aligned.tail(8))
    
    # 3. Store Datasets in SQLite Database
    print("\n[Phase 3] Storing aligned dataset to SQLite Database...")
    db_path = "database/time_series.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        # Save wide format table to SQLite
        df_aligned.to_sql("middle_east_gdp_yoy", conn, if_exists="replace", index=True)
        conn.commit()
        print(f"  -> Saved table 'middle_east_gdp_yoy' to SQLite database: {db_path}")
    except Exception as e:
        print(f"[Warning] Failed to write to SQLite database: {e}")
    finally:
        conn.close()
        
    # 4. Generate Premium Publication-Quality Visualization
    print("\n[Phase 4] Designing and rendering premium line chart...")
    configure_matplotlib_font('FC Vision')
    
    # Set pure white background standard
    plt.rcParams['figure.facecolor'] = '#FFFFFF'
    plt.rcParams['axes.facecolor'] = '#FFFFFF'
    
    # Set soft gridlines
    plt.rcParams['grid.color'] = '#E9ECEF'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.linewidth'] = 0.8
    
    fig, ax = plt.subplots(figsize=(13, 8), dpi=300)
    
    # Curated official NESDC brand color mapping for the 8 Middle East countries
    color_palette = {
        "Saudi Arabia": "#00109E",          # Sapphire Blue (Primary 60%)
        "United Arab Emirates": "#78DED4",  # Caribbean Sea (Secondary 15%)
        "Qatar": "#BFB997",                 # Clay (Support 15%)
        "Kuwait": "#60B1E7",                # Maya Blue (Support 5%)
        "Egypt": "#FFA300",                 # Saffron (Accent highlight 5%)
        "Bahrain": "#005C53",               # Deep Caribbean/Teal Accent
        "Jordan": "#E05A47",                # Red Clay Accent
        "Iran": "#8B6D10"                   # Darker Gold/Clay Accent
    }
    
    # Distinct markers for each country to improve accessibility and visual appeal
    markers = {
        "Saudi Arabia": "o",
        "United Arab Emirates": "s",
        "Qatar": "^",
        "Kuwait": "d",
        "Egypt": "v",
        "Bahrain": "p",
        "Jordan": "h",
        "Iran": "X"
    }
    
    # Plot each country series
    for country in df_aligned.columns:
        series_data = df_aligned[country].dropna()
        if not series_data.empty:
            # Highlight Saudi Arabia and Egypt with thicker lines
            linewidth = 3.0 if country in ["Saudi Arabia", "Egypt"] else 2.0
            ax.plot(
                series_data.index, 
                series_data.values, 
                color=color_palette[country], 
                linewidth=linewidth, 
                marker=markers[country], 
                markersize=5, 
                label=f"{country} (Real GDP %)",
                alpha=0.9
            )
            
    # Add horizontal baseline
    ax.axhline(0, color='#8D99AE', linestyle='-', linewidth=1.2, alpha=0.7)
    
    # Title & Axis labels
    ax.set_title("Middle East Real GDP Growth (YoY % Change)", fontsize=18, fontweight='bold', color='#1D3557', pad=25)
    ax.set_xlabel(None)
    ax.xaxis.label.set_visible(False)
    ax.set_ylabel("Annual GDP Growth (%)", fontsize=12, fontweight='semibold', color='#1D3557', labelpad=12)
    
    # Customize grid and ticks
    ax.grid(True, which='major', axis='both')
    ax.tick_params(axis='both', labelsize=10.5, colors='#1D3557')
    
    # Set dynamic y-axis range to accommodate extreme values nicely
    y_min = df_aligned.min().min() - 1.5
    y_max = df_aligned.max().max() + 1.5
    ax.set_ylim(max(y_min, -20), min(y_max, 25))
    
    # Legend - Positioned snug under the chart to avoid overlapping
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.10),
        ncol=4,
        frameon=True,
        facecolor="#FFFFFF",
        edgecolor="#E9ECEF",
        framealpha=0.9,
        fontsize=10
    )
    
    # Source disclaimer caption at the absolute bottom
    plt.figtext(0.1, 0.02, 
                "Source: CEIC Global Economic Monitor Database. Series transformed to Quarter-End (QE) alignment.\nDisclaimer: Stored in wide-format SQLite database standard 'database/time_series.db' (table: middle_east_gdp_yoy).",
                fontsize=9.5, color='#8D99AE', fontstyle='italic')
    
    plt.tight_layout()
    # Explicitly allocate bottom margin for a tight layout snug with the legend
    fig.subplots_adjust(bottom=0.22)
    
    # Save the premium visualization
    chart_path = "output/chart/middle_east_gdp_yoy.png"
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    plt.savefig(chart_path, dpi=300, facecolor='#FFFFFF', edgecolor='none', bbox_inches='tight')
    plt.close()
    
    print(f"\n[SUCCESS] Saved premium line chart to: {chart_path}")
    print("==================================================")

if __name__ == "__main__":
    main()

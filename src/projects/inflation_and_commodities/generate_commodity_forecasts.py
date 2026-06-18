import os
import sys
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# Add project root to sys.path programmatically
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.api.ceic_client import CeicSession
from src.visualization.charts import configure_matplotlib_font

def main():
    print("==========================================================")
    print("   COMMODITY FORECAST PIPELINE: FETCH, STORE, VISUALIZE   ")
    print("==========================================================")
    
    # 1. Initialize CEIC Session and Authenticate
    session = CeicSession()
    print("[Phase 1] Authenticating with CEIC API...")
    if not session.authenticate():
        print("[FAIL] CEIC Authentication failed.")
        sys.exit(1)
        
    # Map Series ID to Commodity Names
    commodity_map = {
        "354748601": "Gold",
        "303148204": "Silver",
        "354748801": "Platinum",
        "303147804": "Iron Ore",
        "354747901": "Aluminum",
        "354748001": "Copper",
        "303147904": "Lead",
        "354748301": "Nickel",
        "303148004": "Tin",
        "303148104": "Zinc"
    }
    
    commodity_units = {
        "Gold": "USD/Troy oz",
        "Silver": "USD/Troy oz",
        "Platinum": "USD/Troy oz",
        "Iron Ore": "USD/DMTU",
        "Aluminum": "USD/Metric Ton",
        "Copper": "USD/Metric Ton",
        "Lead": "USD/Metric Ton",
        "Nickel": "USD/Metric Ton",
        "Tin": "USD/Metric Ton",
        "Zinc": "USD/Metric Ton"
    }
    
    series_ids = list(commodity_map.keys())
    
    print(f"[Phase 2] Fetching {len(series_ids)} Commodity Forecast series from CEIC...")
    # Fetch with historical extension to get full dataset history and future forecast values
    df_raw = session.get_data(series_ids, with_historical_extension=True, count=10000)
    
    if df_raw.empty:
        print("[FAIL] No data retrieved from CEIC API.")
        sys.exit(1)
        
    print(f"Successfully retrieved {len(df_raw)} raw data points.")
    
    # Map series_id in raw data to Commodity Name
    df_raw['series_id'] = df_raw['series_id'].astype(str)
    df_raw['Commodity'] = df_raw['series_id'].map(commodity_map)
    
    # Filter out missing records
    df_clean = df_raw.dropna(subset=['Commodity', 'date', 'value'])
    
    # 2. Transform into Wide Format
    print("[Phase 3] Transforming series data to Wide Format...")
    df_wide = df_clean.pivot_table(index='date', columns='Commodity', values='value', aggfunc='mean')
    df_wide.index = pd.to_datetime(df_wide.index)
    df_wide = df_wide.sort_index()
    
    # Standardize to Year-End ('YE') representation to clean date indexes
    df_aligned = df_wide.resample('YE').mean()
    df_aligned.index.name = 'date'
    
    print("\n--- Aligned Wide Format Data (Recent Observations) ---")
    print(df_aligned.tail(5))
    
    # 3. Save to SQLite Database (CEIC.db)
    print("\n[Phase 4] Storing aligned dataset to SQLite Database...")
    db_path = "database/CEIC.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        df_aligned.to_sql("world_bank_commodity_forecasts", conn, if_exists="replace", index=True)
        conn.commit()
        print(f"  -> Saved table 'world_bank_commodity_forecasts' to SQLite database: {db_path}")
    except Exception as e:
        print(f"[Warning] Failed to write to SQLite database: {e}")
    finally:
        conn.close()
        
    # 4. Generate Premium Subplot Grid Visualization
    print("\n[Phase 5] Designing and rendering premium grid of subplots...")
    configure_matplotlib_font('FC Vision')
    
    # White background standard
    plt.rcParams['figure.facecolor'] = '#FFFFFF'
    plt.rcParams['axes.facecolor'] = '#FFFFFF'
    plt.rcParams['grid.color'] = '#E9ECEF'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.linewidth'] = 0.8
    
    # Create a 5 rows x 2 columns subplot layout (perfect for page-height reports)
    fig, axes = plt.subplots(5, 2, figsize=(14, 20), dpi=300)
    axes_flat = axes.flatten()
    
    # Curated color scheme mapping for specific commodities
    color_palette = {
        "Gold": "#D4AF37",         # Metallic Gold
        "Silver": "#90A4AE",       # Cool Gray
        "Platinum": "#78909C",     # Blue Gray / Platinum
        "Iron Ore": "#D84315",     # Rust Orange/Red
        "Aluminum": "#00838F",     # Teal Blue
        "Copper": "#D87A50",       # Copper Brown
        "Lead": "#4E342E",         # Dark Brown
        "Nickel": "#558B2F",       # Olive Green
        "Tin": "#00109E",          # NESDC Sapphire Blue
        "Zinc": "#005C53"          # Deep Emerald/Teal
    }
    
    # Order commodities for plotting (Precious first, then Industrial/Base)
    plot_order = [
        "Gold", "Silver", "Platinum", "Iron Ore", 
        "Aluminum", "Copper", "Lead", "Nickel", 
        "Tin", "Zinc"
    ]
    
    # Plot each series on its own axis
    for idx, commodity in enumerate(plot_order):
        ax = axes_flat[idx]
        if commodity in df_aligned.columns:
            series_data = df_aligned[commodity].dropna()
            if not series_data.empty:
                # Plot line and markers
                ax.plot(
                    series_data.index,
                    series_data.values,
                    color=color_palette.get(commodity, "#00109E"),
                    linewidth=2.5,
                    marker="o",
                    markersize=4,
                    alpha=0.9
                )
                
                # Title customized with units
                ax.set_title(f"{commodity} ({commodity_units.get(commodity, 'N/A')})", 
                             fontsize=12, fontweight='bold', color='#1D3557', pad=10)
                
                # Format axes
                ax.grid(True, which='major', axis='both')
                ax.tick_params(axis='both', labelsize=9.5, colors='#1D3557')
                
                # Rotate x-axis labels slightly for better spacing
                plt.setp(ax.get_xticklabels(), rotation=0, ha='center')
                
                # Clean up labels
                ax.set_xlabel(None)
                ax.set_ylabel(None)
        else:
            ax.set_visible(False) # Hide if missing data (should not happen)

    # Super Title for the entire figure
    fig.suptitle("World Bank Commodity Price Forecasts (Nominal)", 
                 fontsize=20, fontweight='bold', color='#1D3557', y=0.97, ha='center')
    
    # Source attribution watermark at the bottom left
    plt.figtext(0.06, 0.02, 
                "Source: World Bank Commodity Price Forecasts (via CEIC Database) | Office of the Chief Economist\nNote: All values are in nominal USD terms as published by the World Bank. Chart formatted to standard NESDC guidelines.",
                fontsize=10, color='#64748b', fontstyle='italic', ha='left')
    
    plt.tight_layout()
    # Explicitly allocate margins for titles and footer
    fig.subplots_adjust(top=0.92, bottom=0.06, hspace=0.35, wspace=0.20)
    
    # Save the premium visualization
    chart_path = "output/chart/commodity_price_forecasts.png"
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    plt.savefig(chart_path, dpi=300, facecolor='#FFFFFF', edgecolor='none', bbox_inches='tight')
    plt.close()
    
    print(f"\n[SUCCESS] Saved premium grid chart to: {chart_path}")
    
    
    series_ids_str = ", ".join(series_ids)
    
    
    print("==========================================================")
    print("   PIPELINE COMPLETION: SUCCESS                           ")
    print("==========================================================")

if __name__ == "__main__":
    main()

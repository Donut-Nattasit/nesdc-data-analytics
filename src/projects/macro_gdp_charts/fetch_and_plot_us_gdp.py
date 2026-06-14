import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import textwrap

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.api.ceic_client import CeicSession

def main():
    print("=== Phase 2 & 3: US GDP Data Acquisition and Visualization ===")
    
    # 1. Initialize CEIC Session and Authenticate
    session = CeicSession()
    if not session.authenticate():
        print("Error: CEIC Authentication failed.", file=sys.stderr)
        sys.exit(1)
    
    # Define Target Series IDs
    # 511278217: Gross Domestic Product: saar (Nominal USD bn)
    # 511279457: Gross Domestic Product: 2017p: saar (Real USD bn)
    # 449521357: Real GDP: QoQ: Quarterly: sa: United States (Growth %)
    series_ids = ["511278217", "511279457", "449521357"]
    
    print(f"Fetching {len(series_ids)} US GDP series from CEIC...")
    df_raw = session.get_data(series_ids, with_historical_extension=True)
    
    if df_raw.empty:
        print("Error: No data retrieved from CEIC API.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Successfully retrieved {len(df_raw)} raw data points.")
    
    # 2. Map Series IDs to Human-Readable Columns
    id_map = {
        511278217: 'us_nominal_gdp',
        511279457: 'us_real_gdp',
        449521357: 'us_real_gdp_growth_qoq'
    }
    
    # Standardize types and map
    df_raw['series_id_int'] = df_raw['series_id'].astype(int)
    df_raw['variable'] = df_raw['series_id_int'].map(id_map)
    
    # Filter out any unmapped variables
    df_mapped = df_raw.dropna(subset=['variable'])
    
    # 3. Clean Dates and Align to Quarter-End ('QE') standard
    print("Aligning quarterly dates to Quarter-End ('QE') standard...")
    df_mapped['date'] = pd.to_datetime(df_mapped['date']) + pd.offsets.QuarterEnd(0)
    
    # 4. Reshape to Wide Format Standard
    print("Pivoting data to Wide Format Standard...")
    wide_df = df_mapped.pivot(index='date', columns='variable', values='value')
    wide_df = wide_df.sort_index()
    
    # Save Wide Format CSV to output/data/
    output_dir = "output/data"
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "us_gdp_ceic.csv")
    wide_df.to_csv(csv_path)
    print(f"Wide-format dataset saved successfully to: {csv_path}")
    print(wide_df.tail(10))
    
    # 5. Professional Visualisation of Real GDP QoQ Growth
    print("Generating premium line chart of Real GDP QoQ growth...")
    plot_df = wide_df['us_real_gdp_growth_qoq'].dropna()
    
    # Filter for data from 2010 onwards
    plot_df = plot_df[plot_df.index >= '2010-01-01']
    
    if plot_df.empty:
        print("Warning: Real GDP Growth QoQ series is empty after 2010. Skipping visualization.")
        return
        
    # Setup Figure and Sleek Premium Style
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Helvetica', 'Arial']
    
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    
    # Grid Styling
    ax.grid(True, which='both', linestyle=':', color='#cbd5e1', linewidth=0.5, alpha=0.7, zorder=0)
    
    # Plot growth line
    line_color = '#0284c7'  # Sophisticated sky blue
    ax.plot(plot_df.index, plot_df.values, color=line_color, linewidth=1.75, label='Real GDP Growth (QoQ %)', zorder=3)
    
    # Shading positive growth in soft blue-teal, negative in soft red
    ax.fill_between(plot_df.index, plot_df.values, 0, where=(plot_df.values >= 0),
                    color='#38bdf8', alpha=0.12, interpolate=True, zorder=2)
    ax.fill_between(plot_df.index, plot_df.values, 0, where=(plot_df.values < 0),
                    color='#f87171', alpha=0.15, interpolate=True, zorder=2)
    
    # Zero line to separate expansion and contraction
    ax.axhline(0, color='#475569', linewidth=1.1, linestyle='-', alpha=0.8, zorder=1)
    
    # Formatting X Axis (Show ticks every 2 years for excellent readability)
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=0, ha='center', fontsize=9.5, color='#475569')
    plt.yticks(fontsize=9.5, color='#475569')
    
    # Programmatic head-room safeguards
    min_val, max_val = plot_df.min(), plot_df.max()
    ax.set_ylim(min_val - 1.0, max_val + 1.5)
    
    # Titles and labels (Preventing overlaps by using precise manual text positioning)
    ax.text(0.0, 1.08, "United States Real GDP Growth (Quarter-on-Quarter)", 
            transform=ax.transAxes, fontsize=14, fontweight='bold', color='#1e293b', ha='left', va='bottom')
    
    subtitle_text = "Bureau of Economic Analysis (via CEIC) | Seasonally Adjusted | 2010-Q1 – 2026-Q1\nShaded Areas: Expansion (Blue) / Contraction (Red)"
    ax.text(0.0, 1.01, subtitle_text, transform=ax.transAxes, fontsize=9.5, color='#64748b', va='bottom', ha='left')
    
    ax.set_xlabel("Year", fontsize=10, labelpad=8, color='#334155')
    ax.set_ylabel("Growth Rate (% QoQ)", fontsize=10, labelpad=8, color='#334155')
    
    # Legend Spacing & Custom Box
    ax.legend(loc='upper right', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', framealpha=0.9, fontsize=9.5)
    
    # Subtle signature/source citation in bottom right
    ax.text(0.99, -0.09, "Source: CEIC Database | Office of the Chief Economist", transform=ax.transAxes,
            fontsize=8.5, color='#94a3b8', ha='right', va='top')
    
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.15, top=0.85)  # Add generous top padding for the title/subtitle

    
    # Save Chart to output/chart/
    chart_dir = "output/chart"
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, "us_real_gdp_growth.png")
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Premium visualization saved successfully to: {chart_path}")
    print("=== Task Complete ===")

if __name__ == '__main__':
    main()

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.api.ceic_client import CeicSession
from src.api.imf_client import IMFClient
from src.visualization.charts import configure_matplotlib_font
from src.utils.registry import add_dataset, add_visualization

def main():
    print("==================================================")
    print("   VIETNAM ECONOMIC GROWTH COMPARATIVE PIPELINE   ")
    print("   (WITH DIRECT WORLD BANK & IMF WORLD BENCHMARKS) ")
    print("==================================================")
    
    # 1. Initialize CEIC Session and Authenticate
    print("[Phase 1] Authenticating with CEIC API...")
    session = CeicSession()
    if not session.authenticate():
        print("[FAIL] CEIC Authentication failed.")
        sys.exit(1)
    print("Successfully authenticated.")

    # Define Target Countries and Series IDs
    gdp_growth_series = {
        "Vietnam": "468137887",
        "United States": "374718167",
        "European Union": "374735017",
        "China": "374827357",
        "India": "565740247",
        "Malaysia": "374732317",
        "Indonesia": "374728867",
        "Philippines": "374742127",
        "Thailand": "374743457"
    }
    
    gdp_pc_series = {
        "Vietnam": "497257947",
        "United States": "405152757",
        "European Union": "217058702",
        "China": "249098601",
        "India": "565740277",
        "Malaysia": "217264302",
        "Indonesia": "249446701",
        "Philippines": "313742001",
        "Thailand": "254909301",
        "World Average": "269121402"  # Added World Average (World Bank sourced via CEIC)
    }
    
    exports_series = {
        "Vietnam": "419518397",
        "United States": "414259457",
        "European Union": "414259317",
        "China": "419360727",
        "India": "419361007",
        "Malaysia": "414259397",
        "Indonesia": "419361047",
        "Philippines": "419357537",
        "Thailand": "419513847"
    }
    
    all_sids = list(gdp_growth_series.values()) + list(gdp_pc_series.values()) + list(exports_series.values())
    
    # 2. Fetch Data
    print(f"\n[Phase 2] Fetching {len(all_sids)} series from CEIC...")
    df_raw = session.get_data(all_sids, with_historical_extension=True)
    
    if df_raw.empty:
        print("[FAIL] Failed to retrieve data from CEIC.")
        sys.exit(1)
    print(f"Retrieved {len(df_raw)} raw data points.")

    # 3. Fetch IMF WEO World Real GDP Growth
    print("\n[Phase 3] Querying live IMF WEO API for World GDP Growth (G001)...")
    imf = IMFClient()
    df_imf_world = imf.get_weo_data(
        country="G001",
        indicator="NGDP_RPCH",
        start_period="2009",
        end_period="2025",
        force_refresh=True
    )
    if not df_imf_world.empty:
        print(f"Successfully retrieved World growth data from IMF WEO: {len(df_imf_world)} points.")
    else:
        print("[Warning] Could not retrieve World GDP growth from IMF API.")
    
    # Ensure directories exist
    os.makedirs("output/data/transformed", exist_ok=True)
    os.makedirs("output/chart", exist_ok=True)

    # Configure Matplotlib fonts and styles
    configure_matplotlib_font('FC Vision')
    plt.rcParams['figure.facecolor'] = '#FFFFFF'
    plt.rcParams['axes.facecolor'] = '#FFFFFF'
    plt.rcParams['grid.color'] = '#E9ECEF'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.linewidth'] = 0.8

    # Define color scheme for standard aesthetics
    color_map = {
        "Vietnam": "#D90429",       # Bold Crimson
        "China": "#FF6B6B",         # Muted Red
        "India": "#FF9F43",         # Muted Orange
        "Malaysia": "#10AC84",      # Muted Teal/Green
        "Indonesia": "#5F27CD",     # Muted Purple
        "Philippines": "#2E86DE",   # Muted Blue
        "Thailand": "#FFC312",      # Muted Yellow
        "United States": "#2C3E50", # Dark Slate
        "European Union": "#7F8C8D", # Gray
        "World Average": "#4A5568"   # Dark Gray for Benchmarks
    }

    # -----------------------------------------------------------------
    # PIPELINE 1: Real GDP Growth (YoY %)
    # -----------------------------------------------------------------
    print("\n[Pipeline 1] Processing Real GDP Growth YoY (Annual)...")
    df_gdp_growth = df_raw[df_raw['series_id'].isin([int(sid) for sid in gdp_growth_series.values()])].copy()
    
    # Map series_id to Country
    sid_to_country_gdp = {int(v): k for k, v in gdp_growth_series.items()}
    df_gdp_growth['country'] = df_gdp_growth['series_id'].map(sid_to_country_gdp)
    df_gdp_growth['year'] = df_gdp_growth['date'].dt.year
    
    # Pivot to Wide format
    df_gdp_growth_wide = df_gdp_growth.pivot(index='year', columns='country', values='value')
    df_gdp_growth_wide = df_gdp_growth_wide.sort_index()
    
    # Merge IMF World growth data
    if not df_imf_world.empty:
        df_imf_world['year'] = df_imf_world['date'].astype(int)
        df_imf_world_series = df_imf_world.set_index('year')['value']
        df_gdp_growth_wide['World Average'] = df_imf_world_series
    
    # Filter for selected range: 2010 - 2025
    df_gdp_growth_final = df_gdp_growth_wide.loc[2010:2025]
    
    # Save CSV
    gdp_growth_csv = "output/data/transformed/vietnam_gdp_growth_comparison.csv"
    df_gdp_growth_final.to_csv(gdp_growth_csv)
    print(f"  -> Saved GDP Growth CSV to: {gdp_growth_csv}")
    
    # Plot Chart 1
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    for country in df_gdp_growth_final.columns:
        y_vals = df_gdp_growth_final[country]
        if country == "Vietnam":
            ax.plot(df_gdp_growth_final.index, y_vals, color=color_map[country], linewidth=3.2,
                    marker='o', markersize=8, markerfacecolor=color_map[country],
                    markeredgecolor='#FFFFFF', markeredgewidth=1.5, zorder=10, label=f"{country} (Focal)")
        elif country == "World Average":
            ax.plot(df_gdp_growth_final.index, y_vals, color=color_map[country], linewidth=2.2, linestyle='--',
                    marker='s', markersize=6, markerfacecolor=color_map[country],
                    markeredgecolor='#FFFFFF', markeredgewidth=1.0, zorder=6, label=country)
        else:
            ax.plot(df_gdp_growth_final.index, y_vals, color=color_map[country], linewidth=1.4,
                    marker='o', markersize=4, alpha=0.75, zorder=2, label=country)
            
    ax.axhline(0, color='#8D99AE', linestyle='-', linewidth=1.0)
    ax.grid(True)
    ax.set_title("Vietnam Real GDP Growth Rate vs. Peers & World Average (2010-2025)", fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel("Annual Real GDP Growth (%)", fontsize=12, fontweight='semibold', labelpad=10)
    ax.set_xlabel("Year", fontsize=12, fontweight='semibold')
    ax.set_xlim(2009.5, 2025.5)
    ax.set_xticks(range(2010, 2026))
    
    # Highlight Vietnam peak rebound in 2022
    if 2022 in df_gdp_growth_final.index:
        val_2022 = df_gdp_growth_final.loc[2022, "Vietnam"]
        ax.annotate(f"Vietnam Rebound: {val_2022:.2f}%", 
                    xy=(2022, val_2022), 
                    xytext=(2022 - 3.2, val_2022 + 1.2),
                    arrowprops=dict(facecolor=color_map["Vietnam"], shrink=0.08, width=1, headwidth=6, headlength=6),
                    fontsize=10, fontweight='bold', color=color_map["Vietnam"],
                    bbox=dict(boxstyle='round,pad=0.3', fc='#FFF0F2', ec=color_map["Vietnam"], alpha=0.9))

    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=5, frameon=True, facecolor="#FFFFFF", edgecolor="#E9ECEF")
    plt.figtext(0.1, 0.01, "Source: CEIC Global Database & IMF World Economic Outlook (WEO) | Office of the Chief Economist", fontsize=9, color='#8D99AE', fontstyle='italic')
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.15)
    
    gdp_growth_chart = "output/chart/vietnam_gdp_growth_comparison.png"
    plt.savefig(gdp_growth_chart, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  -> Saved GDP Growth Chart to: {gdp_growth_chart}")

    # -----------------------------------------------------------------
    # PIPELINE 2: GDP per Capita (USD)
    # -----------------------------------------------------------------
    print("\n[Pipeline 2] Processing GDP per Capita (USD)...")
    df_gdp_pc = df_raw[df_raw['series_id'].isin([int(sid) for sid in gdp_pc_series.values()])].copy()
    
    # Map series_id to Country
    sid_to_country_pc = {int(v): k for k, v in gdp_pc_series.items()}
    df_gdp_pc['country'] = df_gdp_pc['series_id'].map(sid_to_country_pc)
    df_gdp_pc['year'] = df_gdp_pc['date'].dt.year
    
    # Pivot to Wide
    df_gdp_pc_wide = df_gdp_pc.pivot(index='year', columns='country', values='value')
    df_gdp_pc_wide = df_gdp_pc_wide.sort_index()
    
    # Selected range: 2010 - 2024 (as Vietnam/EU end in 2024)
    df_gdp_pc_final = df_gdp_pc_wide.loc[2010:2024]
    
    # Save CSV
    gdp_pc_csv = "output/data/transformed/vietnam_gdp_pc_comparison.csv"
    df_gdp_pc_final.to_csv(gdp_pc_csv)
    print(f"  -> Saved GDP per Capita CSV to: {gdp_pc_csv}")
    
    # Plot Chart 2 (Dual Axis)
    fig, ax1 = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax2 = ax1.twinx()
    
    primary_countries = ["Vietnam", "China", "India", "Malaysia", "Indonesia", "Philippines", "Thailand", "World Average"]
    secondary_countries = ["United States", "European Union"]
    
    # Plot primary countries (Left Axis)
    for country in primary_countries:
        if country not in df_gdp_pc_final.columns:
            continue
        y_vals = df_gdp_pc_final[country]
        if country == "Vietnam":
            ax1.plot(df_gdp_pc_final.index, y_vals, color=color_map[country], linewidth=3.2,
                     marker='o', markersize=8, markerfacecolor=color_map[country],
                     markeredgecolor='#FFFFFF', markeredgewidth=1.5, zorder=10, label=f"{country} (Left Axis - Focal)")
        elif country == "World Average":
            ax1.plot(df_gdp_pc_final.index, y_vals, color=color_map[country], linewidth=2.2, linestyle='--',
                     marker='s', markersize=6, markerfacecolor=color_map[country],
                     markeredgecolor='#FFFFFF', markeredgewidth=1.0, zorder=6, label=f"{country} (Left Axis - Bench)")
        else:
            ax1.plot(df_gdp_pc_final.index, y_vals, color=color_map[country], linewidth=1.4,
                     marker='o', markersize=4, alpha=0.75, zorder=2, label=f"{country} (Left Axis)")
            
    # Plot secondary countries (Right Axis)
    for country in secondary_countries:
        if country not in df_gdp_pc_final.columns:
            continue
        y_vals = df_gdp_pc_final[country]
        ax2.plot(df_gdp_pc_final.index, y_vals, color=color_map[country], linewidth=1.6, linestyle='--',
                 marker='d', markersize=5, alpha=0.85, label=f"{country} (Right Axis)")
        
    ax1.grid(True)
    ax1.set_title("Annual GDP per Capita Comparison (2010-2024)", fontsize=16, fontweight='bold', pad=20)
    ax1.set_ylabel("GDP per Capita (USD) - Left Axis (Peers & World)", fontsize=12, fontweight='semibold', labelpad=10)
    ax2.set_ylabel("GDP per Capita (USD) - Right Axis (US & EU)", fontsize=12, fontweight='semibold', labelpad=10, rotation=270)
    ax1.set_xlabel("Year", fontsize=12, fontweight='semibold')
    ax1.set_xlim(2009.5, 2024.5)
    ax1.set_xticks(range(2010, 2025))
    
    # Combine legends
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=5, frameon=True, facecolor="#FFFFFF", edgecolor="#E9ECEF")
    
    plt.figtext(0.1, 0.01, "Source: CEIC Global/ASEAN Database & World Bank | Note: US & EU plotted on secondary axis; World Average plotted on primary axis", fontsize=9, color='#8D99AE', fontstyle='italic')
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.15)
    
    gdp_pc_chart = "output/chart/vietnam_gdp_pc_comparison.png"
    plt.savefig(gdp_pc_chart, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  -> Saved GDP per Capita Chart to: {gdp_pc_chart}")

    # -----------------------------------------------------------------
    # PIPELINE 3: Annual Value of Total Exports Growth (YoY %)
    # -----------------------------------------------------------------
    print("\n[Pipeline 3] Processing Export Value Growth (YoY %)...")
    df_exp = df_raw[df_raw['series_id'].isin([int(sid) for sid in exports_series.values()])].copy()
    
    # Map series_id to Country
    sid_to_country_exp = {int(v): k for k, v in exports_series.items()}
    df_exp['country'] = df_exp['series_id'].map(sid_to_country_exp)
    df_exp['year'] = df_exp['date'].dt.year
    
    # Count observations per country per year to exclude incomplete years
    df_exp_grouped = df_exp.groupby(['country', 'year']).agg(
        value=('value', 'sum'),
        months_count=('value', 'count')
    ).reset_index()
    
    # Keep only calendar years with exactly 12 months
    df_exp_annual = df_exp_grouped[df_exp_grouped['months_count'] == 12].copy()
    
    # Calculate YoY Growth rate per country
    df_exp_annual = df_exp_annual.sort_values(by=['country', 'year'])
    df_exp_annual['growth_rate'] = df_exp_annual.groupby('country')['value'].pct_change() * 100
    
    # Pivot growth rate to Wide Format
    df_exp_growth_wide = df_exp_annual.pivot(index='year', columns='country', values='growth_rate')
    df_exp_growth_wide = df_exp_growth_wide.sort_index()
    
    # Selected range: 2010 - 2025
    df_exp_growth_final = df_exp_growth_wide.loc[2010:2025]
    
    # Save CSV
    exports_growth_csv = "output/data/transformed/vietnam_exports_growth_comparison.csv"
    df_exp_growth_final.to_csv(exports_growth_csv)
    print(f"  -> Saved Exports Growth CSV to: {exports_growth_csv}")
    
    # Plot Chart 3
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    for country in df_exp_growth_final.columns:
        y_vals = df_exp_growth_final[country]
        if country == "Vietnam":
            ax.plot(df_exp_growth_final.index, y_vals, color=color_map[country], linewidth=3.2,
                    marker='o', markersize=8, markerfacecolor=color_map[country],
                    markeredgecolor='#FFFFFF', markeredgewidth=1.5, zorder=10, label=f"{country} (Focal)")
        else:
            ax.plot(df_exp_growth_final.index, y_vals, color=color_map[country], linewidth=1.4,
                    marker='o', markersize=4, alpha=0.75, zorder=2, label=country)
            
    ax.axhline(0, color='#8D99AE', linestyle='-', linewidth=1.0)
    ax.grid(True)
    ax.set_title("Annual Total Exports Value Growth YoY (%) Comparison (2010-2025)", fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel("Exports Value Growth Rate (YoY %)", fontsize=12, fontweight='semibold', labelpad=10)
    ax.set_xlabel("Year", fontsize=12, fontweight='semibold')
    ax.set_xlim(2009.5, 2025.5)
    ax.set_xticks(range(2010, 2026))
    
    # Highlight Vietnam peak in 2021
    if 2021 in df_exp_growth_final.index:
        val_2021 = df_exp_growth_final.loc[2021, "Vietnam"]
        ax.annotate(f"Vietnam Peak: {val_2021:.1f}%", 
                    xy=(2021, val_2021), 
                    xytext=(2021 - 2.8, val_2021 + 3.5),
                    arrowprops=dict(facecolor=color_map["Vietnam"], shrink=0.08, width=1, headwidth=6, headlength=6),
                    fontsize=10, fontweight='bold', color=color_map["Vietnam"],
                    bbox=dict(boxstyle='round,pad=0.3', fc='#FFF0F2', ec=color_map["Vietnam"], alpha=0.9))

    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=5, frameon=True, facecolor="#FFFFFF", edgecolor="#E9ECEF")
    plt.figtext(0.1, 0.01, "Source: CEIC Global Database | Value of Total Exports resampled from monthly USD values", fontsize=9, color='#8D99AE', fontstyle='italic')
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.15)
    
    exports_growth_chart = "output/chart/vietnam_exports_growth_comparison.png"
    plt.savefig(exports_growth_chart, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  -> Saved Exports Growth Chart to: {exports_growth_chart}")

    # -----------------------------------------------------------------
    # REGISTRY INTEGRATION
    # -----------------------------------------------------------------
    print("\n[Phase 4] Registering datasets and visualizations in PROJECT_STATE.json...")
    # Register datasets
    add_dataset("Vietnam_Peers_Real_GDP_Growth_Annual", "CEIC Global Database & IMF WEO", transformed_path=gdp_growth_csv, status="Ready")
    add_dataset("Vietnam_Peers_GDP_Per_Capita_Yearly", "CEIC Global/ASEAN Database & World Bank", transformed_path=gdp_pc_csv, status="Ready")
    add_dataset("Vietnam_Peers_Exports_Value_Growth_Annual", "CEIC Global Database (Monthly sum to annual)", transformed_path=exports_growth_csv, status="Ready")
    
    # Register visualizations
    add_visualization("Vietnam_Peers_Real_GDP_Growth_Annual_Chart", "Line", "Vietnam_Peers_Real_GDP_Growth_Annual", gdp_growth_chart, status="Rendered")
    add_visualization("Vietnam_Peers_GDP_Per_Capita_Yearly_Chart", "Line", "Vietnam_Peers_GDP_Per_Capita_Yearly", gdp_pc_chart, status="Rendered")
    add_visualization("Vietnam_Peers_Exports_Value_Growth_Annual_Chart", "Line", "Vietnam_Peers_Exports_Value_Growth_Annual", exports_growth_chart, status="Rendered")
    
    print("\n==================================================")
    print("      PIPELINE COMPLETED SUCCESSFULLY             ")
    print("==================================================")

if __name__ == "__main__":
    main()

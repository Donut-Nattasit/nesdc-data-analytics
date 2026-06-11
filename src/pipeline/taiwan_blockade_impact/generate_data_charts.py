import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.visualization.charts import configure_matplotlib_font, save_chart

def main():
    print("Starting data extraction and chart generation for Taiwan Blockade Impact pipeline...")
    
    # Define directories
    data_dir = os.path.join("output", "data", "taiwan_blockade_impact")
    chart_dir = os.path.join("output", "chart", "taiwan_blockade_impact")
    model_dir = os.path.join("output", "model_summary", "taiwan_blockade_impact")
    db_pipeline_dir = os.path.join("database", "taiwan_blockade_impact")
    
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(chart_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(db_pipeline_dir, exist_ok=True)
    
    # Connect to GTA.db
    conn = sqlite3.connect("database/GTA.db")
    
    # ----------------------------------------------------
    # 1. Extraction: Thailand's Bilateral Exposure (2025)
    # ----------------------------------------------------
    print("Extracting Thailand's trade exposure data...")
    df_exposure = pd.read_sql("""
        SELECT Partner_ISO, Trade_Direction, SUM(USD) as Value_USD
        FROM GTA
        WHERE Reporter_ISO = 'TH' AND Partner_ISO IN ('CN', 'JP', 'US', 'TW') AND Year = 2025
        GROUP BY Partner_ISO, Trade_Direction
    """, conn)
    
    # Pivot to wide format
    df_exposure_wide = df_exposure.pivot(index='Partner_ISO', columns='Trade_Direction', values='Value_USD').reset_index()
    # Fill NAs
    df_exposure_wide = df_exposure_wide.fillna(0)
    # Convert to Billion USD
    df_exposure_wide['Export_Billion_USD'] = df_exposure_wide['Export'] / 1e9
    df_exposure_wide['Import_Billion_USD'] = df_exposure_wide['Import'] / 1e9
    
    exposure_csv_path = os.path.join(data_dir, "th_bilateral_exposure_2025.csv")
    df_exposure_wide.to_csv(exposure_csv_path, index=False)
    print(f"Saved exposure data to {exposure_csv_path}")
    
    # ----------------------------------------------------
    # 2. Extraction: Taiwan's Top 10 Exports (2025)
    # ----------------------------------------------------
    print("Extracting Taiwan's top exports data...")
    df_tw_exp = pd.read_sql("""
        SELECT g.HS2_Code, h.HS2_Desc_EN, SUM(g.USD) as Export_Value_USD
        FROM GTA g
        JOIN meta_hs2 h ON g.HS2_Code = h.HS2_Code
        WHERE g.Reporter_ISO = 'TW' AND g.Trade_Direction = 'Export' AND g.Year = 2025
        GROUP BY g.HS2_Code, h.HS2_Desc_EN
        ORDER BY Export_Value_USD DESC
        LIMIT 10
    """, conn)
    
    total_tw_exp = pd.read_sql("""
        SELECT SUM(USD) as total
        FROM GTA
        WHERE Reporter_ISO = 'TW' AND Trade_Direction = 'Export' AND Year = 2025
    """, conn).iloc[0, 0]
    
    df_tw_exp['Share_Pct'] = (df_tw_exp['Export_Value_USD'] / total_tw_exp) * 100
    
    tw_csv_path = os.path.join(data_dir, "taiwan_top_exports_2025.csv")
    df_tw_exp.to_csv(tw_csv_path, index=False)
    print(f"Saved Taiwan top exports to {tw_csv_path}")
    
    # ----------------------------------------------------
    # 3. Extraction: Thailand Electronics (HS 85) Imports (2025)
    # ----------------------------------------------------
    print("Extracting Thailand's electronics imports data...")
    df_electronics = pd.read_sql("""
        SELECT Partner_ISO, SUM(USD) as Import_Value_USD
        FROM GTA
        WHERE Reporter_ISO = 'TH' AND Trade_Direction = 'Import' AND HS2_Code = 85 AND Year = 2025
        GROUP BY Partner_ISO
        ORDER BY Import_Value_USD DESC
    """, conn)
    
    total_el_imp = df_electronics['Import_Value_USD'].sum()
    df_electronics['Share_Pct'] = (df_electronics['Import_Value_USD'] / total_el_imp) * 100
    
    el_csv_path = os.path.join(data_dir, "th_electronics_imports_2025.csv")
    df_electronics.to_csv(el_csv_path, index=False)
    print(f"Saved electronics imports data to {el_csv_path}")
    
    # ----------------------------------------------------
    # 4. Extraction: Thailand Automotive (HS 87) Trade Mapping (2025)
    # ----------------------------------------------------
    print("Extracting Thailand's automotive trade data...")
    df_auto_imp = pd.read_sql("""
        SELECT Partner_ISO, SUM(USD) as Import_Value_USD
        FROM GTA
        WHERE Reporter_ISO = 'TH' AND Trade_Direction = 'Import' AND HS2_Code = 87 AND Year = 2025
        GROUP BY Partner_ISO
        ORDER BY Import_Value_USD DESC
    """, conn)
    total_auto_imp = df_auto_imp['Import_Value_USD'].sum()
    df_auto_imp['Import_Share_Pct'] = (df_auto_imp['Import_Value_USD'] / total_auto_imp) * 100
    
    df_auto_exp = pd.read_sql("""
        SELECT Partner_ISO, SUM(USD) as Export_Value_USD
        FROM GTA
        WHERE Reporter_ISO = 'TH' AND Trade_Direction = 'Export' AND HS2_Code = 87 AND Year = 2025
        GROUP BY Partner_ISO
        ORDER BY Export_Value_USD DESC
    """, conn)
    total_auto_exp = df_auto_exp['Export_Value_USD'].sum()
    df_auto_exp['Export_Share_Pct'] = (df_auto_exp['Export_Value_USD'] / total_auto_exp) * 100
    
    # Save raw CSVs
    auto_imp_csv = os.path.join(data_dir, "th_automotive_imports_2025.csv")
    auto_exp_csv = os.path.join(data_dir, "th_automotive_exports_2025.csv")
    df_auto_imp.to_csv(auto_imp_csv, index=False)
    df_auto_exp.to_csv(auto_exp_csv, index=False)
    print(f"Saved automotive data to {auto_imp_csv} and {auto_exp_csv}")
    
    conn.close()
    
    # ----------------------------------------------------
    # 5. Extraction: Thailand Domestic Automotive Industry Structure (DBD Data)
    # ----------------------------------------------------
    print("Extracting Thailand's domestic automotive industry structure (DBD)...")
    conn_dbd = sqlite3.connect("database/DBD.db")
    df_auto_dbd = pd.read_sql("""
        SELECT f.[รหัสวัตถุประสงค์] as TSIC, a.Description as Desc_EN, 
               COUNT(*) as Num_Firms,
               SUM(f.[รวมรายได้]) as Total_Revenue_THB,
               SUM(f.[สินทรัพย์]) as Total_Assets_THB
        FROM financial_statements f
        LEFT JOIN tsic_activity a ON f.[รหัสวัตถุประสงค์] = a.กิจกรรม
        WHERE f.[รหัสวัตถุประสงค์] LIKE '29%' OR f.[รหัสวัตถุประสงค์] LIKE '309%'
        GROUP BY f.[รหัสวัตถุประสงค์], a.Description
        ORDER BY Total_Revenue_THB DESC
    """, conn_dbd)
    
    # Convert to Billion THB and Billion USD (using 1 USD = 35 THB approximation)
    df_auto_dbd['Total_Revenue_Billion_THB'] = df_auto_dbd['Total_Revenue_THB'] / 1e9
    df_auto_dbd['Total_Assets_Billion_THB'] = df_auto_dbd['Total_Assets_THB'] / 1e9
    df_auto_dbd['Total_Revenue_Billion_USD'] = df_auto_dbd['Total_Revenue_Billion_THB'] / 35.0
    df_auto_dbd['Total_Assets_Billion_USD'] = df_auto_dbd['Total_Assets_Billion_THB'] / 35.0
    
    # Save both for compatibility and detailed drill-down
    auto_dbd_csv = os.path.join(data_dir, "th_auto_firms_summary.csv")
    auto_dbd_csv_detail = os.path.join(data_dir, "th_detailed_auto_subsectors.csv")
    df_auto_dbd.to_csv(auto_dbd_csv, index=False)
    df_auto_dbd.to_csv(auto_dbd_csv_detail, index=False)
    print(f"Saved automotive sub-sector summaries to {auto_dbd_csv} and {auto_dbd_csv_detail}")
    
    conn_dbd.close()
    
    # ----------------------------------------------------
    # Plotting Charts using standard NESDC style
    # ----------------------------------------------------
    print("Rendering charts...")
    configure_matplotlib_font('FC Vision')
    
    # Chart 1: Bilateral Trade Exposure
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    
    # Re-order and rename countries for aesthetics
    exposure_plot_df = df_exposure_wide.copy()
    country_map = {'US': 'United States', 'CN': 'China', 'JP': 'Japan', 'TW': 'Taiwan'}
    exposure_plot_df['Country'] = exposure_plot_df['Partner_ISO'].map(country_map)
    exposure_plot_df = exposure_plot_df.sort_values(by='Import_Billion_USD', ascending=False)
    
    # Grouped bar setup
    import numpy as np
    x_indices = np.arange(len(exposure_plot_df))
    bar_width = 0.35
    
    # NESDC Colors: Blue for Imports, Saffron for Exports
    ax1.bar(x_indices - bar_width/2, exposure_plot_df['Import_Billion_USD'], width=bar_width, label='Imports from Partner', color='#00109E')
    ax1.bar(x_indices + bar_width/2, exposure_plot_df['Export_Billion_USD'], width=bar_width, label='Exports to Partner', color='#FFA300')
    
    ax1.set_xticks(x_indices)
    ax1.set_xticklabels(exposure_plot_df['Country'], fontsize=12, fontweight='medium')
    ax1.set_ylabel('Trade Value (Billion USD)', fontsize=12, fontweight='medium')
    ax1.set_title('Thailand Bilateral Trade Exposure with Key Partners (2025)', fontsize=14, fontweight='bold', pad=20)
    ax1.legend(loc='upper right', frameon=True)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    chart1_path = os.path.join(chart_dir, "trade_exposure.png")
    fig1.savefig(chart1_path, bbox_inches='tight', dpi=150, pil_kwargs={'optimize': True})
    plt.close(fig1)
    print(f"Saved Chart 1 to {chart1_path}")
    
    # Chart 2: Electronics Import Share (Highlighting Taiwan and China)
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    
    electronics_plot = df_electronics.head(8).copy()
    electronics_plot['Country'] = electronics_plot['Partner_ISO'].map(country_map).fillna(electronics_plot['Partner_ISO'])
    
    # Highlight colors: Red for Taiwan (high risk), Orange for China, Sage/Teal for others
    # NESDC brand colors fallback: Navy '#00109E', Teal '#78DED4', Sage '#BFB997', Light Blue '#60B1E7', Saffron '#FFA300'
    colors2 = []
    for iso in electronics_plot['Partner_ISO']:
        if iso == 'TW':
            colors2.append('#e74c3c')  # Geopolitical Risk Red for Taiwan
        elif iso == 'CN':
            colors2.append('#FFA300')  # Saffron for China
        else:
            colors2.append('#00109E')  # Sapphire Blue for others
            
    sns.barplot(data=electronics_plot, x='Share_Pct', y='Country', ax=ax2, palette=colors2)
    
    # Add values on the bars
    for i, p in enumerate(ax2.patches):
        width = p.get_width()
        ax2.text(width + 0.5, p.get_y() + p.get_height()/2 + 0.1, f'{width:.1f}%', ha="left", va="center", fontsize=10, fontweight='bold')
        
    ax2.set_xlabel('Import Value Share (%)', fontsize=12, fontweight='medium')
    ax2.set_ylabel(None)
    ax2.set_title("Thailand's HS 85 Electronics Import Sources (2025)", fontsize=14, fontweight='bold', pad=20)
    ax2.set_xlim(0, 50)
    ax2.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Add annotations about Taiwan and China dominance
    ax2.text(30, 4.5, "Taiwan (20.6%) and China (41.7%)\ncombine for 62.3% of Thailand's\ntotal electronics component imports.", 
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#F8FAFC", edgecolor="#CBD5E1", alpha=0.9),
             fontsize=10, color="#1E293B", ha="left")
             
    chart2_path = os.path.join(chart_dir, "electronics_dependency.png")
    fig2.savefig(chart2_path, bbox_inches='tight', dpi=150, pil_kwargs={'optimize': True})
    plt.close(fig2)
    print(f"Saved Chart 2 to {chart2_path}")
    
    # Chart 3: Automotive Trade Structure Side-by-Side Subplots
    fig3, (ax3_l, ax3_r) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Left subplot: Imports of Components
    auto_imp_plot = df_auto_imp.head(6).copy()
    auto_imp_plot['Country'] = auto_imp_plot['Partner_ISO'].map(country_map).fillna(auto_imp_plot['Partner_ISO'])
    
    colors3_l = ['#FFA300' if iso == 'CN' else ('#BFB997' if iso == 'JP' else '#00109E') for iso in auto_imp_plot['Partner_ISO']]
    sns.barplot(data=auto_imp_plot, x='Import_Share_Pct', y='Country', ax=ax3_l, palette=colors3_l)
    
    for p in ax3_l.patches:
        width = p.get_width()
        ax3_l.text(width + 1.0, p.get_y() + p.get_height()/2 + 0.1, f'{width:.1f}%', ha="left", va="center", fontsize=9, fontweight='bold')
        
    ax3_l.set_xlabel('Import Component Share (%)', fontsize=11)
    ax3_l.set_ylabel(None)
    ax3_l.set_title("A: HS 87 Component Import Sources", fontsize=12, fontweight='bold', pad=10)
    ax3_l.set_xlim(0, 48)
    ax3_l.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Right subplot: Exports of Vehicles
    auto_exp_plot = df_auto_exp.head(6).copy()
    auto_exp_plot['Country'] = auto_exp_plot['Partner_ISO'].map(country_map).fillna(auto_exp_plot['Partner_ISO'])
    # Add Australia mapping manually
    auto_exp_plot.loc[auto_exp_plot['Partner_ISO'] == 'AU', 'Country'] = 'Australia'
    auto_exp_plot.loc[auto_exp_plot['Partner_ISO'] == 'PH', 'Country'] = 'Philippines'
    auto_exp_plot.loc[auto_exp_plot['Partner_ISO'] == 'VN', 'Country'] = 'Vietnam'
    auto_exp_plot.loc[auto_exp_plot['Partner_ISO'] == 'MY', 'Country'] = 'Malaysia'
    
    colors3_r = ['#00109E' for _ in range(len(auto_exp_plot))]
    # Highlight Australia which is the largest export destination
    if len(auto_exp_plot) > 0:
        colors3_r[0] = '#78DED4'  # Teal for Australia export exposure
        
    sns.barplot(data=auto_exp_plot, x='Export_Share_Pct', y='Country', ax=ax3_r, palette=colors3_r)
    
    for p in ax3_r.patches:
        width = p.get_width()
        ax3_r.text(width + 0.5, p.get_y() + p.get_height()/2 + 0.1, f'{width:.1f}%', ha="left", va="center", fontsize=9, fontweight='bold')
        
    ax3_r.set_xlabel('Vehicle Export Share (%)', fontsize=11)
    ax3_r.set_ylabel(None)
    ax3_r.set_title("B: HS 87 Vehicle Export Destinations", fontsize=12, fontweight='bold', pad=10)
    ax3_r.set_xlim(0, 25)
    ax3_r.grid(axis='x', linestyle='--', alpha=0.7)
    
    fig3.suptitle("Thailand's Automotive Sector Trade Mapping (2025)", fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    fig3.subplots_adjust(top=0.86)
    
    chart3_path = os.path.join(chart_dir, "automotive_mapping.png")
    fig3.savefig(chart3_path, bbox_inches='tight', dpi=150, pil_kwargs={'optimize': True})
    plt.close(fig3)
    print(f"Saved Chart 3 to {chart3_path}")
    
    # ----------------------------------------------------
    # 6. Chart 4: Detailed Automotive Sub-sectors by Revenue
    # ----------------------------------------------------
    print("Rendering Chart 4: Detailed Automotive Sub-sectors by Revenue...")
    fig4, ax4 = plt.subplots(figsize=(12, 7))
    
    # Sort and take top 10 from df_auto_dbd
    auto_sub_plot = df_auto_dbd.head(10).copy()
    
    # Capitalize descriptions and clean them up
    auto_sub_plot['Clean_Desc'] = auto_sub_plot['Desc_EN'].str.replace(
        "The production of ", "", regex=False
    ).str.replace(
        "production of ", "", regex=False
    ).str.replace(
        ", which are not classified elsewhere.", "", regex=False
    ).str.replace(
        "which is not classified elsewhere", "", regex=False
    ).str.strip().str.title()
    
    # Shorten very long names
    auto_sub_plot.loc[auto_sub_plot['TSIC'] == '29309', 'Clean_Desc'] = 'Other Parts & Accessories'
    
    # Colors: Highlight the electronic choke point (29302) and assembly lines (29102)
    colors4 = []
    for tsic in auto_sub_plot['TSIC']:
        if tsic == '29302':
            colors4.append('#FFA300')  # Saffron (highlighting choke point)
        elif tsic in ['29102', '29101', '30911']:
            colors4.append('#00109E')  # Sapphire Blue (assembly/engine)
        else:
            colors4.append('#60B1E7')  # Light Blue (parts/bodies)
            
    sns.barplot(data=auto_sub_plot, x='Total_Revenue_Billion_THB', y='Clean_Desc', ax=ax4, palette=colors4)
    
    # Add values on the bars (in both THB and USD)
    for p in ax4.patches:
        width = p.get_width()
        if width > 0:
            usd_val = width / 35.0
            ax4.text(width + 20, p.get_y() + p.get_height()/2 + 0.1, 
                     f'{width:,.1f}B THB (${usd_val:,.1f}B)', 
                     ha="left", va="center", fontsize=9, fontweight='bold')
            
    ax4.set_xlabel('Annual Revenue (Billion THB)', fontsize=12, fontweight='medium')
    ax4.set_ylabel(None)
    ax4.set_title("Thailand's Top Automotive Manufacturing Sub-sectors by Revenue", fontsize=14, fontweight='bold', pad=25)
    ax4.set_xlim(0, 1850)
    ax4.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Add footnote about highlights
    plt.figtext(0.1, 0.01, "*Note: Saffron highlights Vehicle Electronics (TSIC 29302), the critical semiconductor-dependent choke point. Navy highlights vehicle assembly and engine manufacturing.",
                fontsize=9, style='italic', color='#475569')
    
    chart4_path = os.path.join(chart_dir, "automotive_subsectors_revenue.png")
    fig4.savefig(chart4_path, bbox_inches='tight', dpi=150, pil_kwargs={'optimize': True})
    plt.close(fig4)
    print(f"Saved Chart 4 to {chart4_path}")
    
    print("Data extraction and chart rendering completed successfully!")

if __name__ == "__main__":
    main()

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from src.visualization.charts import configure_matplotlib_font

# Official NESDC Palette mapping (module-level constants — safe to import)
c_sapphire = "#00109E"  # Primary
c_caribbean = "#78DED4" # Secondary support
c_clay = "#BFB997"      # Neutral comparison
c_maya = "#60B1E7"      # Accent
c_saffron = "#FFA300"   # Highlight


def run_charts(data_path: str = "output/data/ex_im_price_forecast/export_import_price_monthly_wide.csv"):
    """Render all 9 ex/im price charts. Call this explicitly or run the module directly."""
    # 1. Setup styling
    configure_matplotlib_font('FC Vision')
    plt.rcParams['figure.facecolor'] = '#FFFFFF'
    plt.rcParams['axes.facecolor'] = '#FFFFFF'
    plt.rcParams['grid.color'] = '#E9ECEF'
    plt.rcParams['grid.alpha'] = 0.7

    # 2. Load data
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"{data_path} not found. Run prepare_data.py first.")

    df = pd.read_csv(data_path, index_col=0, parse_dates=True)
    df = df.sort_index()

    # Ensure output directory exists
    os.makedirs("output/chart/ex_im_price_forecast", exist_ok=True)

    # Compute YoY growth rates
    df['export_yoy'] = df['ceic_expi_composite'].pct_change(12) * 100
    df['import_yoy'] = df['ceic_impi_composite'].pct_change(12) * 100

    # ----------------------------------------------------
    # Chart 1: Composite indices & YoY Growth (2 vertical subplots)
    # ----------------------------------------------------
    print("Plotting Chart 1: Composite indices & YoY Growth...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Top subplot: Price Indices (Sapphire for Export, Saffron or Caribbean for Import)
    ax1.plot(df.index, df['ceic_expi_composite'], label='Export Price Index (Composite)', color=c_sapphire, linewidth=2)
    ax1.plot(df.index, df['ceic_impi_composite'], label='Import Price Index (Composite)', color=c_caribbean, linewidth=2)
    ax1.set_ylabel('Index (2012=100)', fontsize=12)
    ax1.set_title('Export & Import Price Indices (Composite)', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left', frameon=True)
    ax1.grid(True)

    # Bottom subplot: YoY Growth
    ax2.plot(df.index, df['export_yoy'], label='Export Price YoY Growth', color=c_sapphire, linewidth=2, linestyle='--')
    ax2.plot(df.index, df['import_yoy'], label='Import Price YoY Growth', color=c_caribbean, linewidth=2, linestyle='--')
    ax2.axhline(0, color='black', linewidth=0.8, linestyle='-')
    ax2.set_ylabel('YoY Growth (%)', fontsize=12)
    ax2.set_title('Year-on-Year Growth Rate', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper left', frameon=True)
    ax2.grid(True)

    # Format X axis
    ax2.xaxis.set_major_locator(mdates.YearLocator(2))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=30, ha='right')

    plt.tight_layout()
    chart1_path = "output/chart/ex_im_price_forecast/export_import_price_composite_yoy.png"
    plt.savefig(chart1_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved Chart 1 to {chart1_path}")

# ----------------------------------------------------
    # Chart 2: Export Price Index by component (Line chart)
    # ----------------------------------------------------
    print("Plotting Chart 2: Export Price by Component...")
    ex_comps = {
        "ceic_expi_principal_manuf": "Principal Manufacturing Product (MP)",
        "ceic_expi_agro_industrial": "Agro Industrial Product (AIP)",
        "ceic_expi_agricultural": "Agricultural Product (AP)",
        "ceic_expi_mineral_fuel": "Mineral Product and Fuel (MF)"
    }
    colors_ex = [c_sapphire, c_caribbean, c_clay, c_maya]

    plt.figure(figsize=(12, 6))
    for (col, label), color in zip(ex_comps.items(), colors_ex):
        plt.plot(df.index, df[col], label=label, color=color, linewidth=2)

    plt.title('Export Price Index by Component', fontsize=14, fontweight='bold')
    plt.ylabel('Index (2012=100)', fontsize=12)
    plt.legend(loc='upper left', frameon=True)
    plt.grid(True)
    plt.gca().xaxis.set_major_locator(mdates.YearLocator(2))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    chart2_path = "output/chart/ex_im_price_forecast/export_import_price_export_price_by_component.png"
    plt.savefig(chart2_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved Chart 2 to {chart2_path}")

    # ----------------------------------------------------
    # Chart 3: Import Price Index by component (Line chart)
    # ----------------------------------------------------
    print("Plotting Chart 3: Import Price by Component...")
    im_comps = {
        "ceic_impi_raw_materials": "Raw Material and Intermediate Goods (RM)",
        "ceic_impi_capital_goods": "Capital Goods (CA)",
        "ceic_impi_fuel": "Fuel Product (FP)",
        "ceic_impi_consumer_goods": "Consumer Goods (CO)",
        "ceic_impi_vehicle_equip": "Vehicle and Equipment (VE)"
    }
    colors_im = [c_sapphire, c_caribbean, c_maya, c_clay, c_saffron]

    plt.figure(figsize=(12, 6))
    for (col, label), color in zip(im_comps.items(), colors_im):
        plt.plot(df.index, df[col], label=label, color=color, linewidth=2)

    plt.title('Import Price Index by Component', fontsize=14, fontweight='bold')
    plt.ylabel('Index (2012=100)', fontsize=12)
    plt.legend(loc='upper left', frameon=True)
    plt.grid(True)
    plt.gca().xaxis.set_major_locator(mdates.YearLocator(2))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    chart3_path = "output/chart/ex_im_price_forecast/export_import_price_import_price_by_component.png"
    plt.savefig(chart3_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved Chart 3 to {chart3_path}")

    # ----------------------------------------------------
    # Chart 4: Export Price Weight (2 horizontal subplots)
    # ----------------------------------------------------
    print("Plotting Chart 4: Export Weights Structure...")
    # Weights start from Jan 2001
    df_wgt = df.loc["2001-01-01":]

    ex_wgt_cols = ["wgt_expi_principal_manuf", "wgt_expi_agro_industrial", "wgt_expi_agricultural", "wgt_expi_mineral_fuel"]
    ex_wgt_labels = ["Principal Manufacturing (MP)", "Agro Industrial (AIP)", "Agricultural (AP)", "Mineral & Fuel (MF)"]
    ex_wgt_colors = [c_sapphire, c_caribbean, c_clay, c_maya]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8.5), gridspec_kw={'width_ratios': [2, 1]})

    # Stacked area plot of weights
    ax1.stackplot(df_wgt.index, 
                  [df_wgt[c] for c in ex_wgt_cols], 
                  labels=ex_wgt_labels, 
                  colors=ex_wgt_colors, 
                  alpha=0.85)
    ax1.set_title('Export Price Weights Structure Over Time', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Weight Share (%)', fontsize=12)
    ax1.set_ylim(0, 100)
    # Move legend to the bottom of the left chart instead of inside
    ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=True, fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_locator(mdates.YearLocator(3))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.set_xlabel(None)

    # Most recent weights (latest month)
    latest_date = df_wgt.index[-1]
    latest_ex_wgts = df_wgt.loc[latest_date, ex_wgt_cols]

    # Create sorted weights dataframe (largest to smallest)
    latest_ex_df = pd.DataFrame({
        'col': ex_wgt_cols,
        'label': ex_wgt_labels,
        'weight': latest_ex_wgts.values,
        'color': ex_wgt_colors
    }).sort_values(by='weight', ascending=False)

    bars = ax2.bar(latest_ex_df['label'], latest_ex_df['weight'], color=latest_ex_df['color'], alpha=0.9, edgecolor='black', linewidth=0.8)
    ax2.set_title(f'Latest Export Weights ({latest_date.strftime("%B %Y")})', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Weight (%)', fontsize=12)
    ax2.set_ylim(0, max(latest_ex_df['weight']) * 1.15)
    ax2.grid(True, axis='y', alpha=0.3)

    # Add number labels at the top of each bar
    for bar in bars:
        height = bar.get_height()
        ax2.annotate(f'{height:.2f}%',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.setp(ax2.get_xticklabels(), rotation=30, ha='right')
    # Adjust bottom spacing to fit bottom legend of ax1
    fig.subplots_adjust(bottom=0.25)

    chart4_path = "output/chart/ex_im_price_forecast/export_import_price_export_weights_structure.png"
    plt.savefig(chart4_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved Chart 4 to {chart4_path}")

    # ----------------------------------------------------
    # Chart 5: Import Price Weight (2 horizontal subplots)
    # ----------------------------------------------------
    print("Plotting Chart 5: Import Weights Structure...")
    im_wgt_cols = ["wgt_impi_raw_materials", "wgt_impi_capital_goods", "wgt_impi_fuel", "wgt_impi_consumer_goods", "wgt_impi_vehicle_equip"]
    im_wgt_labels = ["Raw Material (RM)", "Capital Goods (CA)", "Fuel Product (FP)", "Consumer Goods (CO)", "Vehicle & Equip (VE)"]
    im_wgt_colors = [c_sapphire, c_caribbean, c_maya, c_clay, c_saffron]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8.5), gridspec_kw={'width_ratios': [2, 1]})

    # Stacked area plot of weights
    ax1.stackplot(df_wgt.index, 
                  [df_wgt[c] for c in im_wgt_cols], 
                  labels=im_wgt_labels, 
                  colors=im_wgt_colors, 
                  alpha=0.85)
    ax1.set_title('Import Price Weights Structure Over Time', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Weight Share (%)', fontsize=12)
    ax1.set_ylim(0, 100)
    # Move legend to the bottom of the left chart instead of inside
    ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=True, fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_locator(mdates.YearLocator(3))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.set_xlabel(None)

    # Most recent weights (latest month)
    latest_im_wgts = df_wgt.loc[latest_date, im_wgt_cols]

    # Create sorted weights dataframe (largest to smallest)
    latest_im_df = pd.DataFrame({
        'col': im_wgt_cols,
        'label': im_wgt_labels,
        'weight': latest_im_wgts.values,
        'color': im_wgt_colors
    }).sort_values(by='weight', ascending=False)

    bars = ax2.bar(latest_im_df['label'], latest_im_df['weight'], color=latest_im_df['color'], alpha=0.9, edgecolor='black', linewidth=0.8)
    ax2.set_title(f'Latest Import Weights ({latest_date.strftime("%B %Y")})', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Weight (%)', fontsize=12)
    ax2.set_ylim(0, max(latest_im_df['weight']) * 1.15)
    ax2.grid(True, axis='y', alpha=0.3)

    # Add number labels at the top of each bar
    for bar in bars:
        height = bar.get_height()
        ax2.annotate(f'{height:.2f}%',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.setp(ax2.get_xticklabels(), rotation=30, ha='right')
    # Adjust bottom spacing to fit bottom legend of ax1
    fig.subplots_adjust(bottom=0.25)

    chart5_path = "output/chart/ex_im_price_forecast/export_import_price_import_weights_structure.png"
    plt.savefig(chart5_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved Chart 5 to {chart5_path}")

    # ----------------------------------------------------
    # Chart 6: Export Growth Contribution (Stacked bar) - Plot only after 2016
    # ----------------------------------------------------
    print("Plotting Chart 6: Export Growth Contribution (After 2016)...")
    # Filter data to only include dates after 2016
    df_contrib = df.loc["2016-01-01":].copy()

    # Recalculate contributions using history for 12-month lags
    contrib_ex_cols = []
    ex_comps_mapping = {
        "ceic_expi_principal_manuf": "principal_manuf",
        "ceic_expi_agro_industrial": "agro_industrial",
        "ceic_expi_agricultural": "agricultural",
        "ceic_expi_mineral_fuel": "mineral_fuel"
    }

    for col_price, comp in ex_comps_mapping.items():
        col_wgt = f"wgt_expi_{comp}"
        col_contrib = f"contrib_expi_{comp}"

        w_t12 = df.loc[df_contrib.index - pd.DateOffset(months=12), col_wgt].values
        p_t = df_contrib[col_price].values
        p_t12 = df.loc[df_contrib.index - pd.DateOffset(months=12), col_price].values
        p_comp_t12 = df.loc[df_contrib.index - pd.DateOffset(months=12), "ceic_expi_composite"].values

        df_contrib[col_contrib] = w_t12 * (p_t - p_t12) / p_comp_t12
        contrib_ex_cols.append(col_contrib)

    # Pro-rata scaling to match CEIC total export growth exactly
    yoy_total_ex = df_contrib["export_yoy"]
    contrib_sum_ex = df_contrib[contrib_ex_cols].sum(axis=1)
    diff_ex = yoy_total_ex - contrib_sum_ex

    for col in contrib_ex_cols:
        comp_name = col.replace("contrib_expi_", "")
        wgt_col = f"wgt_expi_{comp_name}"
        wgt_t12_share = df.loc[df_contrib.index - pd.DateOffset(months=12), wgt_col].values / 100.0
        df_contrib[col] = df_contrib[col] + diff_ex * wgt_t12_share

    # Plot
    plt.figure(figsize=(14, 7))
    pos_contrib = df_contrib[contrib_ex_cols].clip(lower=0)
    neg_contrib = df_contrib[contrib_ex_cols].clip(upper=0)

    bottom_pos = np.zeros(len(df_contrib))
    bottom_neg = np.zeros(len(df_contrib))

    # Align order of plotting with ex_wgt_colors
    for col, label, color in zip(contrib_ex_cols, ex_wgt_labels, ex_wgt_colors):
        # Plot positive bars
        plt.bar(df_contrib.index, pos_contrib[col], bottom=bottom_pos, width=20, label=label, color=color, alpha=0.85)
        bottom_pos += pos_contrib[col].values

        # Plot negative bars
        plt.bar(df_contrib.index, neg_contrib[col], bottom=bottom_neg, width=20, color=color, alpha=0.85)
        bottom_neg += neg_contrib[col].values

    # Plot the total growth line
    plt.plot(df_contrib.index, df_contrib["export_yoy"], label="Export Price YoY Growth (Total)", color="black", linewidth=2.5)

    # Set dynamic y-limits to prevent bar clipping
    max_y = max(bottom_pos.max(), df_contrib["export_yoy"].max())
    min_y = min(bottom_neg.min(), df_contrib["export_yoy"].min())
    y_padding_top = max_y * 0.15 if max_y > 0 else 0.5
    y_padding_bottom = abs(min_y) * 0.15 if min_y < 0 else 0.5
    plt.ylim(min_y - y_padding_bottom, max_y + y_padding_top)

    plt.title("Contributions of Components to Export Price Index YoY Growth (Since 2016)", fontsize=14, fontweight="bold")
    plt.ylabel("YoY Growth & Contribution (% points)", fontsize=12)
    plt.axhline(0, color='black', linewidth=0.8)
    # Hide redundant x-label
    plt.gca().set_xlabel(None)
    plt.gca().xaxis.label.set_visible(False)
    # Bottom legend snug fit
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.11), frameon=True, ncol=2)
    plt.grid(True, alpha=0.3)
    plt.gca().xaxis.set_major_locator(mdates.YearLocator(1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=30, ha='right')
    plt.subplots_adjust(bottom=0.18)

    chart6_path = "output/chart/ex_im_price_forecast/export_import_price_export_contribution_to_growth.png"
    plt.savefig(chart6_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved Chart 6 to {chart6_path}")

    # ----------------------------------------------------
    # Chart 7: Import Growth Contribution (Stacked bar) - Plot only after 2016
    # ----------------------------------------------------
    print("Plotting Chart 7: Import Growth Contribution (After 2016)...")
    contrib_im_cols = []
    im_comps_mapping = {
        "ceic_impi_raw_materials": "raw_materials",
        "ceic_impi_capital_goods": "capital_goods",
        "ceic_impi_fuel": "fuel",
        "ceic_impi_consumer_goods": "consumer_goods",
        "ceic_impi_vehicle_equip": "vehicle_equip"
    }

    for col_price, comp in im_comps_mapping.items():
        col_wgt = f"wgt_impi_{comp}"
        col_contrib = f"contrib_impi_{comp}"

        w_t12 = df.loc[df_contrib.index - pd.DateOffset(months=12), col_wgt].values
        p_t = df_contrib[col_price].values
        p_t12 = df.loc[df_contrib.index - pd.DateOffset(months=12), col_price].values
        p_comp_t12 = df.loc[df_contrib.index - pd.DateOffset(months=12), "ceic_impi_composite"].values

        df_contrib[col_contrib] = w_t12 * (p_t - p_t12) / p_comp_t12
        contrib_im_cols.append(col_contrib)

    # Pro-rata scaling to match CEIC total import growth exactly
    yoy_total_im = df_contrib["import_yoy"]
    contrib_sum_im = df_contrib[contrib_im_cols].sum(axis=1)
    diff_im = yoy_total_im - contrib_sum_im

    for col in contrib_im_cols:
        comp_name = col.replace("contrib_impi_", "")
        wgt_col = f"wgt_impi_{comp_name}"
        wgt_t12_share = df.loc[df_contrib.index - pd.DateOffset(months=12), wgt_col].values / 100.0
        df_contrib[col] = df_contrib[col] + diff_im * wgt_t12_share

    # Plot
    plt.figure(figsize=(14, 7))
    pos_contrib_im = df_contrib[contrib_im_cols].clip(lower=0)
    neg_contrib_im = df_contrib[contrib_im_cols].clip(upper=0)

    bottom_pos_im = np.zeros(len(df_contrib))
    bottom_neg_im = np.zeros(len(df_contrib))

    for col, label, color in zip(contrib_im_cols, im_wgt_labels, im_wgt_colors):
        # Plot positive bars
        plt.bar(df_contrib.index, pos_contrib_im[col], bottom=bottom_pos_im, width=20, label=label, color=color, alpha=0.85)
        bottom_pos_im += pos_contrib_im[col].values

        # Plot negative bars
        plt.bar(df_contrib.index, neg_contrib_im[col], bottom=bottom_neg_im, width=20, color=color, alpha=0.85)
        bottom_neg_im += neg_contrib_im[col].values

    # Plot the total growth line
    plt.plot(df_contrib.index, df_contrib["import_yoy"], label="Import Price YoY Growth (Total)", color="black", linewidth=2.5)

    # Set dynamic y-limits to prevent bar clipping
    max_y_im = max(bottom_pos_im.max(), df_contrib["import_yoy"].max())
    min_y_im = min(bottom_neg_im.min(), df_contrib["import_yoy"].min())
    y_padding_top_im = max_y_im * 0.15 if max_y_im > 0 else 0.5
    y_padding_bottom_im = abs(min_y_im) * 0.15 if min_y_im < 0 else 0.5
    plt.ylim(min_y_im - y_padding_bottom_im, max_y_im + y_padding_top_im)

    plt.title("Contributions of Components to Import Price Index YoY Growth (Since 2016)", fontsize=14, fontweight="bold")
    plt.ylabel("YoY Growth & Contribution (% points)", fontsize=12)
    plt.axhline(0, color='black', linewidth=0.8)
    plt.gca().set_xlabel(None)
    plt.gca().xaxis.label.set_visible(False)
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.11), frameon=True, ncol=2)
    plt.grid(True, alpha=0.3)
    plt.gca().xaxis.set_major_locator(mdates.YearLocator(1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=30, ha='right')
    plt.subplots_adjust(bottom=0.18)

    chart7_path = "output/chart/ex_im_price_forecast/export_import_price_import_contribution_to_growth.png"
    plt.savefig(chart7_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved Chart 7 to {chart7_path}")

    # ----------------------------------------------------
    # Chart 8: Export Sub-component Weights (Horizontal bar)
    # ----------------------------------------------------
    print("Plotting Chart 8: Export Sub-component Weights...")
    latest_date = df.index[-1]
    print(f"Latest date for sub-component weights: {latest_date.strftime('%Y-%m-%d')}")

    ex_sub_mapping = {
        "wgt_expi_ap_agriculture": ("AP: Agriculture", "AP", c_clay),
        "wgt_expi_ap_fishery": ("AP: Fishery", "AP", c_clay),
        "wgt_expi_ap_livestock": ("AP: Livestock", "AP", c_clay),
        "wgt_expi_aip_preserved_aquatic": ("AIP: Prepared/Preserved Aquatic", "AIP", c_caribbean),
        "wgt_expi_aip_cane_sugar": ("AIP: Cane Sugar and Molasses", "AIP", c_caribbean),
        "wgt_expi_aip_canned_fruit": ("AIP: Canned Fruit", "AIP", c_caribbean),
        "wgt_expi_aip_canned_veg": ("AIP: Canned Vegetable", "AIP", c_caribbean),
        "wgt_expi_mp_textile": ("MP: Textile", "MP", c_sapphire),
        "wgt_expi_mp_gems_jewelry": ("MP: Gems and Jewelry", "MP", c_sapphire),
        "wgt_expi_mp_electrical_equip": ("MP: Electrical Equipment", "MP", c_sapphire),
        "wgt_expi_mp_electronic_machine": ("MP: Electronic Machine", "MP", c_sapphire),
        "wgt_expi_mp_iron_steel": ("MP: Iron and Steel", "MP", c_sapphire),
        "wgt_expi_mp_polymer": ("MP: Polymer", "MP", c_sapphire),
        "wgt_expi_mp_plastic_product": ("MP: Plastic Product", "MP", c_sapphire),
        "wgt_expi_mp_chemical_product": ("MP: Chemical Product", "MP", c_sapphire),
        "wgt_expi_mp_rubber_product": ("MP: Rubber Product", "MP", c_sapphire),
        "wgt_expi_mp_vehicles_parts": ("MP: Vehicles and Parts", "MP", c_sapphire),
        "wgt_expi_mf_lpg": ("MF: LPG", "MF", c_maya),
        "wgt_expi_mf_crude_oil": ("MF: Crude Oil", "MF", c_maya),
        "wgt_expi_mf_refined_fuel": ("MF: Refined Fuel", "MF", c_maya)
    }

    # Extract latest weights
    ex_rows = []
    for col, (label, parent, color) in ex_sub_mapping.items():
        val = df.loc[latest_date, col] if col in df.columns else 0.0
        ex_rows.append({
            'col': col,
            'label': label,
            'parent': parent,
            'weight': val,
            'color': color
        })

    df_ex_sub = pd.DataFrame(ex_rows).sort_values(by='weight', ascending=False)

    plt.figure(figsize=(12, 10))
    bars = plt.barh(df_ex_sub['label'], df_ex_sub['weight'], color=df_ex_sub['color'], edgecolor='black', linewidth=0.6, alpha=0.9)
    plt.gca().invert_yaxis()  # Put largest at the top

    # Add value labels
    for bar in bars:
        width = bar.get_width()
        plt.annotate(f'{width:.2f}%',
                     xy=(width, bar.get_y() + bar.get_height() / 2),
                     xytext=(5, 0),
                     textcoords="offset points",
                     ha='left', va='center', fontsize=9, fontweight='bold')

    plt.title(f'Export Weights by Sub-component ({latest_date.strftime("%B %Y")})', fontsize=14, fontweight='bold')
    plt.xlabel('Weight (%)', fontsize=12)
    plt.xlim(0, max(df_ex_sub['weight']) * 1.15)
    plt.grid(True, axis='x', alpha=0.3)

    # Add custom legend
    import matplotlib.patches as mpatches
    legend_patches = [
        mpatches.Patch(color=c_sapphire, label='Principal Manufacturing (MP)'),
        mpatches.Patch(color=c_caribbean, label='Agro Industrial (AIP)'),
        mpatches.Patch(color=c_clay, label='Agricultural Product (AP)'),
        mpatches.Patch(color=c_maya, label='Mineral & Fuel (MF)')
    ]
    plt.legend(handles=legend_patches, loc='lower right', frameon=True, fontsize=10)

    plt.tight_layout()
    chart8_path = "output/chart/ex_im_price_forecast/export_import_price_export_subcomponent_weights.png"
    plt.savefig(chart8_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved Chart 8 to {chart8_path}")

    # ----------------------------------------------------
    # Chart 9: Import Sub-component Weights (Horizontal bar)
    # ----------------------------------------------------
    print("Plotting Chart 9: Import Sub-component Weights...")
    im_sub_mapping = {
        "wgt_impi_fp_crude_oil": ("FP: Crude Oil", "FP", c_maya),
        "wgt_impi_fp_finished_oil": ("FP: Finished Oil", "FP", c_maya),
        "wgt_impi_fp_natural_gas": ("FP: Natural Gas", "FP", c_maya),
        "wgt_impi_ca_metal_manufacture": ("CA: Metal Manufacture", "CA", c_caribbean),
        "wgt_impi_ca_machinery": ("CA: Machinery & Parts", "CA", c_caribbean),
        "wgt_impi_ca_electrical_machinery": ("CA: Electrical Machinery & Parts", "CA", c_caribbean),
        "wgt_impi_ca_computer_parts": ("CA: Computer & Parts", "CA", c_caribbean),
        "wgt_impi_ca_scientific_appliances": ("CA: Scientific Appliances", "CA", c_caribbean),
        "wgt_impi_rm_aquatic_animal": ("RM: Aquatic Animal", "RM", c_sapphire),
        "wgt_impi_rm_vegetable_product": ("RM: Vegetable Product", "RM", c_sapphire),
        "wgt_impi_rm_chemical_product": ("RM: Chemical Product", "RM", c_sapphire),
        "wgt_impi_rm_plastic_product": ("RM: Plastic Product", "RM", c_sapphire),
        "wgt_impi_rm_gems_jewelry": ("RM: Precious Stones and Jewelry", "RM", c_sapphire),
        "wgt_impi_rm_iron_steel": ("RM: Iron and Steel", "RM", c_sapphire),
        "wgt_impi_rm_other_metal": ("RM: Other Metal Ore and Product", "RM", c_sapphire),
        "wgt_impi_rm_fertilizer_pesticide": ("RM: Fertilizer and Pesticide", "RM", c_sapphire),
        "wgt_impi_rm_electrical_electronic": ("RM: Electrical & Electronic Parts", "RM", c_sapphire),
        "wgt_impi_co_dairy_product": ("CO: Dairy Product", "CO", c_clay),
        "wgt_impi_co_apparel": ("CO: Apparel & Footwear", "CO", c_clay),
        "wgt_impi_co_pharmaceutical": ("CO: Pharmaceuticals", "CO", c_clay),
        "wgt_impi_co_manufactured_article": ("CO: Manufactured Article", "CO", c_clay),
        "wgt_impi_co_household_appliance": ("CO: Household Appliances", "CO", c_clay),
        "wgt_impi_ve_bus_truck": ("VE: Bus and Truck", "VE", c_saffron),
        "wgt_impi_ve_vehicle_parts": ("VE: Vehicle Parts and Accessories", "VE", c_saffron)
    }

    # Extract latest weights
    im_rows = []
    for col, (label, parent, color) in im_sub_mapping.items():
        val = df.loc[latest_date, col] if col in df.columns else 0.0
        im_rows.append({
            'col': col,
            'label': label,
            'parent': parent,
            'weight': val,
            'color': color
        })

    df_im_sub = pd.DataFrame(im_rows).sort_values(by='weight', ascending=False)

    plt.figure(figsize=(12, 11))
    bars = plt.barh(df_im_sub['label'], df_im_sub['weight'], color=df_im_sub['color'], edgecolor='black', linewidth=0.6, alpha=0.9)
    plt.gca().invert_yaxis()  # Put largest at the top

    # Add value labels
    for bar in bars:
        width = bar.get_width()
        plt.annotate(f'{width:.2f}%',
                     xy=(width, bar.get_y() + bar.get_height() / 2),
                     xytext=(5, 0),
                     textcoords="offset points",
                     ha='left', va='center', fontsize=9, fontweight='bold')

    plt.title(f'Import Weights by Sub-component ({latest_date.strftime("%B %Y")})', fontsize=14, fontweight='bold')
    plt.xlabel('Weight (%)', fontsize=12)
    plt.xlim(0, max(df_im_sub['weight']) * 1.15)
    plt.grid(True, axis='x', alpha=0.3)

    # Add custom legend
    legend_patches_im = [
        mpatches.Patch(color=c_sapphire, label='Raw Materials (RM)'),
        mpatches.Patch(color=c_caribbean, label='Capital Goods (CA)'),
        mpatches.Patch(color=c_maya, label='Fuel Product (FP)'),
        mpatches.Patch(color=c_clay, label='Consumer Goods (CO)'),
        mpatches.Patch(color=c_saffron, label='Vehicle & Equip (VE)')
    ]
    plt.legend(handles=legend_patches_im, loc='lower right', frameon=True, fontsize=10)

    plt.tight_layout()
    chart9_path = "output/chart/ex_im_price_forecast/export_import_price_import_subcomponent_weights.png"
    plt.savefig(chart9_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved Chart 9 to {chart9_path}")

    print("All 9 charts plotted successfully with custom visual upgrades!")



if __name__ == '__main__':
    run_charts()

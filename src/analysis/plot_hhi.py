import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.visualization.charts import configure_matplotlib_font, save_chart

def main():
    # 1. Setup styling
    configure_matplotlib_font('FC Vision')
    plt.rcParams['figure.facecolor'] = '#FFFFFF'
    plt.rcParams['axes.facecolor'] = '#FFFFFF'
    plt.rcParams['grid.color'] = '#E9ECEF'
    plt.rcParams['grid.alpha'] = 0.7
    
    # Official NESDC Palette mapping
    c_sapphire = "#00109E"  # Primary
    c_caribbean = "#78DED4" # Secondary support
    c_saffron = "#FFA300"   # Highlight
    c_maya = "#60B1E7"      # Accent
    c_red = "#E74C3C"       # Warning/Highlight
    
    # Load data
    data_path = "output/data/hhi_tsic4.csv"
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Please run compute_hhi.py first.")
        sys.exit(1)
        
    df = pd.read_csv(data_path, dtype={'tsic4': str})
    
    # Ensure output chart directory exists
    os.makedirs("output/chart", exist_ok=True)
    
    # ----------------------------------------------------
    # Chart 1: Top 10 Most Concentrated Industries (HHI)
    # Filter for industries with at least 20 active firms to make it meaningful
    # ----------------------------------------------------
    print("Plotting Chart 1: Top 10 concentrated industries...")
    min_firms = 20
    df_filtered = df[df['active_firms'] >= min_firms].copy()
    df_top10 = df_filtered.sort_values(by='hhi', ascending=False).head(10)
    
    # Create descriptions with TSIC codes for the y-labels
    df_top10['label'] = df_top10.apply(lambda r: f"{r['tsic4']} - {r['desc_en'][:35]}..." if len(r['desc_en']) > 35 else f"{r['tsic4']} - {r['desc_en']}", axis=1)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Create a gradient color for the bars from sapphire to maya
    colors = sns.color_palette("Blues_r", n_colors=15)[2:12]
    
    bars = ax.barh(df_top10['label'], df_top10['hhi'], color=colors, edgecolor='black', linewidth=0.6, alpha=0.9)
    ax.invert_yaxis()  # Put largest HHI at the top
    
    # Add HHI value labels at the end of each bar
    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'{width:,.0f}',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(8, 0),
                    textcoords="offset points",
                    ha='left', va='center', fontsize=10, fontweight='bold', color='#1E293B')
                    
    # HHI concentration threshold lines
    ax.axvline(2500, color=c_red, linestyle='--', linewidth=1.2, label='Highly Concentrated Threshold (HHI >= 2,500)')
    ax.axvline(1500, color=c_saffron, linestyle='--', linewidth=1.2, label='Moderately Concentrated Threshold (HHI >= 1,500)')
    
    ax.set_title(f'Top 10 Most Concentrated Industries\n(TSIC 4-Digit, Min. {min_firms} Active Firms)', fontsize=15, fontweight='bold', pad=15)
    ax.set_xlabel('Herfindahl-Hirschman Index (HHI)', fontsize=12, fontweight='medium', labelpad=10)
    ax.set_xlim(0, 10700)
    ax.grid(True, axis='x', linestyle='-', alpha=0.4)
    ax.legend(loc='lower right', frameon=True, fontsize=10)
    
    # Add source watermark
    fig.text(0.08, 0.01, "Source: Department of Business Development (DBD) Database, Fiscal Year 2566", fontsize=9, color='#64748B', ha='left')
    
    plt.tight_layout()
    chart1_path = save_chart(fig, "hhi_top10_concentrated.png")
    print(f"Saved Chart 1 to {chart1_path}")
    
    # ----------------------------------------------------
    # Chart 2: HHI vs. Number of Active Firms (Scatter Plot)
    # ----------------------------------------------------
    print("Plotting Chart 2: HHI vs. Number of Active Firms...")
    
    # Only plot industries with at least 1 active firm and positive revenue
    df_scatter = df[df['firms_with_revenue'] > 0].copy()
    
    fig, ax = plt.subplots(figsize=(11, 7))
    
    # Scatter plot: X is firms_with_revenue, Y is HHI
    # Size is proportional to total revenue (log scale for size to avoid giant bubbles)
    df_scatter['bubble_size'] = np.log10(df_scatter['total_revenue'] + 1) * 35
    
    scatter = ax.scatter(
        df_scatter['firms_with_revenue'], 
        df_scatter['hhi'], 
        s=df_scatter['bubble_size'], 
        c=df_scatter['hhi'], 
        cmap='Blues', 
        alpha=0.75, 
        edgecolors='black', 
        linewidths=0.6
    )
    
    # Add labels for a few prominent or interesting industries
    # E.g., largest by revenue, or extremely high HHI
    to_label = [
        # Highly concentrated and large
        df_scatter[df_scatter['active_firms'] >= 20].sort_values(by='hhi', ascending=False).head(3),
        # Largest by revenue
        df_scatter.sort_values(by='total_revenue', ascending=False).head(3)
    ]
    df_label = pd.concat(to_label).drop_duplicates(subset=['tsic4'])
    
    # Use adjust_text if available, otherwise simple annotation
    for idx, row in df_label.iterrows():
        ax.annotate(
            f"{row['tsic4']} ({row['desc_en'][:20]}...)" if len(row['desc_en']) > 20 else f"{row['tsic4']} ({row['desc_en']})",
            xy=(row['firms_with_revenue'], row['hhi']),
            xytext=(10, 10),
            textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color='#475569', lw=0.8),
            fontsize=8.5,
            fontweight='semibold',
            color='#1E293B',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#CBD5E1", lw=0.5, alpha=0.85)
        )
        
    # Concentration threshold line
    ax.axhline(2500, color=c_red, linestyle='--', linewidth=1.2, label='Highly Concentrated Threshold (HHI >= 2,500)')
    ax.axhline(1500, color=c_saffron, linestyle='--', linewidth=1.2, label='Moderately Concentrated Threshold (HHI >= 1,500)')
    
    # X-axis scale can be log to see the dense distribution at low firm counts
    ax.set_xscale('log')
    ax.set_title('Market Concentration (HHI) vs. Number of Active Firms', fontsize=15, fontweight='bold', pad=15)
    ax.set_xlabel('Number of Active Firms (Log Scale)', fontsize=12, fontweight='medium', labelpad=10)
    ax.set_ylabel('Herfindahl-Hirschman Index (HHI)', fontsize=12, fontweight='medium', labelpad=10)
    ax.set_ylim(-200, 10500)
    ax.grid(True, which='both', linestyle='-', alpha=0.3)
    ax.legend(loc='upper right', frameon=True, fontsize=10)
    
    # Add size explanation
    fig.text(0.08, 0.01, "* Bubble size is proportional to log10 of total industry revenue. Source: DBD Database, FY 2566", fontsize=9, color='#64748B', ha='left')
    
    plt.tight_layout()
    chart2_path = save_chart(fig, "hhi_vs_firms_scatter.png")
    print(f"Saved Chart 2 to {chart2_path}")
    
    print("All HHI charts plotted successfully!")

if __name__ == '__main__':
    main()

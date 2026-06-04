import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.visualization.charts import configure_matplotlib_font
from src.utils.registry import add_visualization, add_dataset

def main():
    project_root = Path(__file__).resolve().parents[2]
    db_path = project_root / "database" / "core" / "DBD.db"
    
    if not db_path.exists():
        print(f"Error: Database {db_path} not found.")
        sys.exit(1)
        
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(str(db_path))
    
    # Query summing 'รวมรายได้' (Total Revenue) for each S/M/L and TSIC Category, including both Thai and English descriptions
    query = """
    SELECT 
        tc.หมวดใหญ่ AS category_code,
        tc.Description AS category_desc_en,
        tc.คำอธิบาย AS category_desc_th,
        f.firm_size,
        SUM(f.รวมรายได้) as total_revenue
    FROM financial_statements f
    JOIN tsic_mapping tm ON f.รหัสวัตถุประสงค์ = tm.กิจกรรม
    JOIN tc AS tc ON tm.หมวดใหญ่ = tc.หมวดใหญ่
    GROUP BY tc.หมวดใหญ่, tc.Description, tc.คำอธิบาย, f.firm_size
    """
    
    # Wait, in DBD.db, is the table named 'tsic_category' or 'tc'?
    # In load_tsic.py, we wrote: "หมวดใหญ่": {"table": "tsic_category", ...}
    # So the table is 'tsic_category', not 'tc'!
    # Let's write the query correctly with 'tsic_category'.
    query = """
    SELECT 
        tc.หมวดใหญ่ AS category_code,
        tc.Description AS category_desc_en,
        tc.คำอธิบาย AS category_desc_th,
        f.firm_size,
        SUM(f.รวมรายได้) as total_revenue
    FROM financial_statements f
    JOIN tsic_mapping tm ON f.รหัสวัตถุประสงค์ = tm.กิจกรรม
    JOIN tsic_category tc ON tm.หมวดใหญ่ = tc.หมวดใหญ่
    GROUP BY tc.หมวดใหญ่, tc.Description, tc.คำอธิบาย, f.firm_size
    """
    
    print("Executing SQL query...")
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print("Formatting and pivoting data...")
    pivot_df = df.pivot(
        index=['category_code', 'category_desc_en', 'category_desc_th'], 
        columns='firm_size', 
        values='total_revenue'
    ).fillna(0)
    
    for col in ['S', 'M', 'L']:
        if col not in pivot_df.columns:
            pivot_df[col] = 0.0
            
    # Add totals and calculate shares of revenue
    pivot_df['Total_Revenue'] = pivot_df['S'] + pivot_df['M'] + pivot_df['L']
    pivot_df['S_rev_share'] = pivot_df['S'] / pivot_df['Total_Revenue']
    pivot_df['M_rev_share'] = pivot_df['M'] / pivot_df['Total_Revenue']
    pivot_df['L_rev_share'] = pivot_df['L'] / pivot_df['Total_Revenue']
    
    result_df = pivot_df.reset_index()
    
    # Sort alphabetically by category code (A to U)
    result_df = result_df.sort_values(by='category_code', ascending=True)
    
    # Save CSV
    csv_dir = project_root / "output" / "data" / "transformed"
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_path = csv_dir / "revenue_share_by_category.csv"
    
    print(f"Saving CSV to: {csv_path}")
    result_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    # Register the output CSV dataset
    add_dataset(
        series_id="Revenue Shares by TSIC Category",
        source="Department of Business Development (DBD)",
        raw_path="database/core/DBD.db",
        transformed_path="output/data/transformed/revenue_share_by_category.csv",
        status="Ready"
    )
    
    # Configure Matplotlib fonts and styles to ensure Thai renders correctly
    print("Configuring Matplotlib font styles...")
    configure_matplotlib_font('FC Vision')
    
    # Create y-axis label combining Thai description and code
    y_labels = result_df.apply(lambda r: f"{r['category_desc_th']} ({r['category_code']})", axis=1).tolist()
    
    # NESDC brand colors
    colors = {
        'S': '#14B8A6',  # Caribbean Sea/Teal
        'M': '#FFA300',  # Saffron/Amber
        'L': '#00109E'   # Sapphire Blue
    }
    
    # Large size with wide margin for long Thai descriptions
    fig, ax = plt.subplots(figsize=(16, 8.5))
    
    # Coordinates
    y_pos = np.arange(len(result_df))
    
    # 100% shares
    s_shares = result_df['S_rev_share'].values
    m_shares = result_df['M_rev_share'].values
    l_shares = result_df['L_rev_share'].values
    
    # Draw horizontal bars
    rects_s = ax.barh(y_pos, s_shares, color=colors['S'], label='S (Small)', edgecolor='white', height=0.7)
    rects_m = ax.barh(y_pos, m_shares, left=s_shares, color=colors['M'], label='M (Medium)', edgecolor='white', height=0.7)
    rects_l = ax.barh(y_pos, l_shares, left=s_shares + m_shares, color=colors['L'], label='L (Large)', edgecolor='white', height=0.7)
    
    # Set labels and styling
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels, fontsize=10.5, fontweight='bold')
    ax.invert_yaxis()  # Invert so largest L is on top
    
    # Set X-axis to percent format
    ax.set_xlim(0, 1.0)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, tick: f"{val*100:.0f}%"))
    ax.tick_params(axis='x', labelsize=10)
    
    # Grid lines
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    
    # Add text labels inside bars with minimum threshold (5%) to prevent overlapping in narrow bars
    for idx, (s, m, l) in enumerate(zip(s_shares, m_shares, l_shares)):
        # Label for S
        if s > 0.05:
            ax.text(s / 2, idx, f"{s*100:.1f}%", va='center', ha='center', color='white', fontsize=10, fontweight='bold')
        # Label for M
        if m > 0.05:
            ax.text(s + m / 2, idx, f"{m*100:.1f}%", va='center', ha='center', color='white', fontsize=10, fontweight='bold')
        # Label for L
        if l > 0.05:
            ax.text(s + m + l / 2, idx, f"{l*100:.1f}%", va='center', ha='center', color='white', fontsize=10, fontweight='bold')
            
    # Labels, Title, and Subtitle adhering to NESDC standard spacing rules
    ax.set_xlabel('สัดส่วนรายได้ (%) / Share of Revenue (%)', fontsize=12, fontweight='bold', labelpad=10)
    
    # Isolate Title and Subtitle to prevent overlaps, while keeping spacing tight
    fig.suptitle('โครงสร้างรายได้แบ่งตามขนาดธุรกิจและหมวดธุรกิจ TSIC', fontsize=16, fontweight='bold', x=0.5, y=0.96, ha='center')
    ax.set_title('คำนวณจากผลรวมรายได้ เรียงตามหมวดธุรกิจ (A - U)', 
                 fontsize=11, color='#64748b', pad=10, loc='center')
    
    # Source attribution at bottom-left corner of the canvas (NESDC Standard)
    fig.text(0.04, 0.03, 'ที่มา: กรมพัฒนาธุรกิจการค้า (DBD)', fontsize=9.5, color='#64748b', ha='left')
    
    # Position bottom legend to avoid overlap with xlabel and bottom grid
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.11), ncol=3, frameon=True, facecolor='white', edgecolor='#E5E7EB', fontsize=11)
    
    # Use tight_layout dynamically, then adjust margins to ensure long Thai text fits on the left
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.18, top=0.88, left=0.38, right=0.95)
    
    chart_path = project_root / "output" / "chart" / "revenue_share_by_category.png"
    
    print(f"Saving chart to: {chart_path}")
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Register the visualization
    add_visualization(
        name="Revenue Shares by TSIC Category",
        chart_type="Stacked Horizontal Bar Chart",
        source_data="database/core/DBD.db",
        png_path="output/chart/revenue_share_by_category.png"
    )
    
    print("Plotting and export complete!")

if __name__ == "__main__":
    main()

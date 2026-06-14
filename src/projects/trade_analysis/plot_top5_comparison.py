import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def plot_refreshed_comparison():
    print("Generating refreshed YoY comparison chart...")
    
    project_root = Path.cwd()
    summary_path = project_root / 'output/data/thailand_top5_exports_refreshed_summary.csv'
    chart_dir = project_root / 'output/chart'
    chart_dir.mkdir(parents=True, exist_ok=True)
    chart_path = chart_dir / 'thailand_top5_exports_comparison_refreshed.png'
    
    if not summary_path.exists():
        print(f"[Error] Summary file not found at {summary_path}")
        return
        
    df = pd.read_csv(summary_path)
    
    # Sort by 2026 period value to make chart look structured and logical
    df = df.sort_values(by='usd_2026_period', ascending=False)
    
    # Values in Billions USD for clean axis presentation
    val_2025 = df['usd_2025_period'] / 1e9
    val_2026 = df['usd_2026_period'] / 1e9
    labels = df['hs_code'] + "\n" + df['sector_name'].str.wrap(20)
    growth = df['yoy_growth_pct']
    months_label = df['months_included'].iloc[0] # e.g. "Jan-05" (meaning Jan-May)
    
    # Styling variables
    color_2025 = '#64748B'  # Slate Grey
    color_2026 = '#0EA5E9'  # Vibrant Electric Sky Blue
    
    # Create plot figure
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    fig.patch.set_facecolor('#F8FAFC') # Soft off-white premium canvas
    ax.set_facecolor('#FFFFFF')
    
    x = np.arange(len(labels))
    width = 0.35
    
    # Plot grouped bars
    rects1 = ax.bar(x - width/2, val_2025, width, label='2025 Period (Jan-May)', color=color_2025, edgecolor='none', alpha=0.85, zorder=3)
    rects2 = ax.bar(x + width/2, val_2026, width, label='2026 Period (Jan-May)', color=color_2026, edgecolor='none', alpha=0.95, zorder=3)
    
    # Customise axes, gridlines and borders
    ax.set_ylabel('Export Value (Billion USD)', fontsize=11, fontweight='semibold', color='#334155', labelpad=12)
    ax.set_title(f"Thailand's Top 5 Exports: YoY Performance Comparison\nPeriod: {months_label} (January–May) 2025 vs 2026", 
                 fontsize=14, fontweight='bold', color='#1E293B', pad=24)
    
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.5, fontweight='semibold', color='#475569', rotation=0)
    
    # Premium grid styling
    ax.grid(axis='y', linestyle='--', alpha=0.4, color='#CBD5E1', zorder=0)
    
    # Remove outer spines for clean modern look
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color('#94A3B8')
    ax.spines['bottom'].set_linewidth(1.2)
    
    # Add YoY Growth annotations on top of the bars
    for i, rect in enumerate(rects2):
        height = rect.get_height()
        yoy = growth.iloc[i]
        
        # Color code the YoY sign
        color_yoy = '#10B981' if yoy >= 0 else '#EF4444' # Emerald green vs Crimson red
        sign = '+' if yoy >= 0 else ''
        
        ax.annotate(f"{sign}{yoy:.2f}% YoY",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 6),  # 6 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9.5, fontweight='bold',
                    color=color_yoy, bbox=dict(boxstyle="round,pad=0.3", fc="#FFFFFF", ec=color_yoy, lw=1, alpha=0.9), zorder=5)
        
    # Legend customization
    legend = ax.legend(loc='upper right', frameon=True, facecolor='#FFFFFF', edgecolor='#E2E8F0', framealpha=0.9, fontsize=10)
    for text in legend.get_texts():
        text.set_color('#334155')
        text.set_weight('semibold')
        
    # Layout adjustments
    plt.tight_layout()
    
    # Save the rendered PNG image
    plt.savefig(chart_path, dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    
    print(f"[Success] Generated high-fidelity comparison chart at {chart_path}")

if __name__ == "__main__":
    plot_refreshed_comparison()

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# Reconfigure stdout to UTF-8 for safe logging
sys.stdout.reconfigure(encoding='utf-8')

def plot_iran_war_impact():
    print("Initializing Post-Iran War Price Disruption Analyzer...")
    project_root = Path.cwd()
    
    # Paths
    csv_path = project_root / 'output/data/moc_prices/moc_prices_wide.csv'
    chart_dir = project_root / 'output/chart'
    chart_dir.mkdir(parents=True, exist_ok=True)
    chart_path = chart_dir / 'indexed_prices_post_iran_war.png'

    if not csv_path.exists():
        print(f"Error: Wide master dataset not found at {csv_path}. Run transform script first.")
        return

    # Load wide master dataset
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Define base date and filter data
    base_date_str = "2026-02-27"
    base_date = pd.to_datetime(base_date_str)
    
    print(f"Filtering dataset starting from Base Date: {base_date_str}...")
    df_filtered = df[df['date'] >= base_date].copy()
    
    if df_filtered.empty:
        print(f"Error: No data found on or after {base_date_str}.")
        return
        
    # Verify base date exists in dataset
    if base_date not in df_filtered['date'].values:
        # Find the closest date
        closest_date = df_filtered['date'].min()
        print(f"[Warning] Base date {base_date_str} not exactly in dataset. Using closest start date: {closest_date.strftime('%Y-%m-%d')}")
        base_date = closest_date
        base_date_str = closest_date.strftime('%Y-%m-%d')

    # Define variables to analyze
    # NOTE: Thai characters stripped from labels to prevent glyph-box rendering failures
    # with non-Thai fonts (DejaVu Sans / Arial do not contain Thai Unicode glyphs)
    target_series = {
        'P11009_avg': 'Chicken (P11009 - Whole Chicken)',
        'P11037_avg': 'Pork (P11037 - Red Meat / Hip Cut)',
        'P11028_avg': 'Egg (P11028 - Egg No. 3)'
    }

    # Verify all series exist in the wide dataset
    missing_cols = [col for col in target_series if col not in df_filtered.columns]
    if missing_cols:
        print(f"Error: Missing columns in wide dataset: {missing_cols}")
        return

    # Base values for indexing
    base_row = df_filtered[df_filtered['date'] == base_date].iloc[0]
    
    print("\n--- Base Date Prices (2026-02-27) ---")
    for col, name in target_series.items():
        base_price = base_row[col]
        print(f"- {name}: {base_price:.2f} THB")
    
    # Calculate Indexed Prices
    print("\nCalculating indices (Base: 2026-02-27 = 100)...")
    for col in target_series:
        base_val = base_row[col]
        if base_val == 0:
            base_val = 1.0  # Safe division fallback
        df_filtered[f"{col}_indexed"] = (df_filtered[col] / base_val) * 100.0

    # ----------------------------------------------------
    # Professional Styling & Plotting
    # ----------------------------------------------------
    print("Rendering premium-grade line chart...")
    # Use FC Vision font registered from assets/ (falls back to DejaVu Sans)
    # NOTE: Do NOT embed Thai characters in labels when using non-Thai fonts
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
    
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')  # Strict white per workspace mandate
    ax.set_facecolor('#ffffff')

    # Colors for lines
    colors = {
        'P11009_avg_indexed': '#1d4ed8',  # Sleek Dark Blue (Chicken)
        'P11037_avg_indexed': '#d97706',  # Warm Amber (Pork)
        'P11028_avg_indexed': '#dc2626'   # Crimson Red (Egg)
    }
    
    line_styles = {
        'P11009_avg_indexed': '-',
        'P11037_avg_indexed': '-',
        'P11028_avg_indexed': '-'
    }
    
    markers = {
        'P11009_avg_indexed': 'o',
        'P11037_avg_indexed': '^',
        'P11028_avg_indexed': 's'
    }

    # Plot each line
    most_recent_row = df_filtered.iloc[-1]
    most_recent_date_str = most_recent_row['date'].strftime('%Y-%m-%d')
    
    for col, label in target_series.items():
        indexed_col = f"{col}_indexed"
        line_color = colors[indexed_col]
        
        # Plot full trajectory
        line = ax.plot(
            df_filtered['date'], 
            df_filtered[indexed_col], 
            label=label,
            color=line_color,
            linestyle=line_styles[indexed_col],
            linewidth=2.5,
            alpha=0.95
        )
        
        # Add slight shadow to lines for premium feel
        ax.plot(
            df_filtered['date'], 
            df_filtered[indexed_col], 
            color=line_color,
            linestyle=line_styles[indexed_col],
            linewidth=4.5,
            alpha=0.15
        )
        
        # Annotate final values with smart vertical offsets to prevent label collision
        # Series-specific offsets (in points) to separate labels when Y-values are close
        label_offsets = {
            'P11009_avg_indexed': (14,  10),   # Chicken: push slightly up
            'P11037_avg_indexed': (14, -18),   # Pork:    push down to clear Chicken
            'P11028_avg_indexed': (14,   0),   # Egg:     far above, no collision risk
        }
        x_off, y_off = label_offsets[indexed_col]
        final_val = most_recent_row[indexed_col]
        final_price_raw = most_recent_row[col]
        ax.annotate(
            f"{final_val:.1f}\n({final_price_raw:.1f} THB)",
            xy=(df_filtered['date'].max(), final_val),
            xytext=(x_off, y_off),
            textcoords='offset points',
            color=line_color,
            weight='bold',
            size=9.5,
            va='center'
        )
        
        # Add marker at base date and final date
        ax.scatter([base_date], [100.0], color=line_color, s=50, zorder=5)
        ax.scatter([df_filtered['date'].max()], [final_val], color=line_color, s=50, zorder=5)

    # Gridlines and aesthetics
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='#e5e7eb', zorder=1)
    ax.axhline(100.0, color='#9ca3af', linestyle='-', linewidth=1.2, zorder=2, alpha=0.8) # 100 baseline
    
    # Title & Subtitle (Aesthetic hierarchy)
    plt.title("Consumer Price Trajectories Post-Disruption\n", fontsize=16, weight='bold', color='#1f2937', loc='left', pad=15)
    ax.text(
        0.0, 1.05, 
        f"Indexed Daily Product Prices (Base: Feb 27, 2026 = 100) | Trajectory to {most_recent_date_str}", 
        transform=ax.transAxes, 
        fontsize=10.5, 
        color='#4b5563', 
        weight='medium'
    )

    # Legend
    legend = ax.legend(
        loc='upper left', 
        frameon=True, 
        facecolor='#ffffff', 
        edgecolor='#e5e7eb',
        fontsize=10, 
        labelspacing=0.8
    )
    legend.get_frame().set_boxstyle('round,pad=0.5')

    # Date formatting on X axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d, %Y'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=10))
    fig.autofmt_xdate()

    # Labels — X-axis label hidden on temporal axes (Gap-Free Spacing Rule)
    ax.set_ylabel("Price Index (Base = 100)", fontsize=11, weight='bold', color='#374151', labelpad=10)
    ax.set_xlabel(None)
    ax.xaxis.label.set_visible(False)

    # Clean borders (spines)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color('#d1d5db')
        
    ax.tick_params(colors='#4b5563', labelsize=9.5)
    
    # Margins and paddings
    plt.tight_layout()
    ax.set_xlim(base_date - pd.Timedelta(days=2), df_filtered['date'].max() + pd.Timedelta(days=8))
    
    # Save the premium figure
    plt.savefig(chart_path, facecolor=fig.get_facecolor(), bbox_inches='tight')
    print(f"[Success] Chart successfully rendered and saved to: {chart_path.relative_to(project_root)}")
    
    # Present final findings in log
    print("\n--- Final Indexed Values (2026-05-26) ---")
    for col, label in target_series.items():
        indexed_col = f"{col}_indexed"
        chg = most_recent_row[indexed_col] - 100.0
        sign = "+" if chg >= 0 else ""
        print(f"- {label}: {most_recent_row[indexed_col]:.1f} ({sign}{chg:.2f}%) | Raw: {most_recent_row[col]:.2f} THB")

if __name__ == '__main__':
    plot_iran_war_impact()

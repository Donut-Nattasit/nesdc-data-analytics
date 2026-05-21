import pandas as pd
import altair as alt
import os
import sys
from pathlib import Path

# Add project root to path to import local charts library
sys.path.append(str(Path.cwd()))
from src.visualization.charts import save_chart

def generate_grouped_bar_chart():
    project_root = Path.cwd()
    data_path = project_root / 'output/data/transformed' / 'thailand_top5_exports_growth.csv'
    
    # Load data
    df = pd.read_csv(data_path)
    
    # Let's create a compact category name for the chart: "HS XX (Short Desc)"
    # Shorten the very long HS descriptions to fit on axes
    short_descriptions = {
        85: "Electrical Machinery & Electronics",
        84: "Mechanical Machinery & Boilers",
        87: "Vehicles & Parts",
        71: "Precious Stones & Gems",
        40: "Rubber & Rubber Articles"
    }
    
    df['Short_Desc'] = df['HS2_Code'].map(short_descriptions)
    df['Category'] = df.apply(lambda row: f"HS {row['HS2_Code']:02d}\n{row['Short_Desc']}", axis=1)
    
    # Restructure into long format for Altair grouped bar chart
    long_data = []
    for _, row in df.iterrows():
        long_data.append({
            'Category': row['Category'],
            'Year': '2025 (Jan-Feb)',
            'Value_Billion_USD': row['USD_2025_Period'] / 1e9,
            'YoY_Text': ''
        })
        long_data.append({
            'Category': row['Category'],
            'Year': '2026 (Jan-Feb)',
            'Value_Billion_USD': row['USD_2026_Period'] / 1e9,
            'YoY_Text': f"{row['YoY_Change_Pct']:+.1f}%"
        })
        
    plot_df = pd.DataFrame(long_data)
    
    # Build Altair Grouped Bar Chart
    # Grouped bar charts in Altair are built using X offset (faceted X)
    # The main X-axis is Category, and we use xOffset='Year:N' to place bars side-by-side!
    chart = alt.Chart(plot_df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X('Category:N', title='HS2 Category', axis=alt.Axis(labelAngle=0, labelAlign='center')),
        y=alt.Y('Value_Billion_USD:Q', title='Export Value (USD Billion)', scale=alt.Scale(zero=True)),
        xOffset='Year:N',
        color=alt.Color('Year:N', 
                        scale=alt.Scale(domain=['2025 (Jan-Feb)', '2026 (Jan-Feb)'], range=['#94a3b8', '#0284c7']),
                        title='Period'),
        tooltip=[
            alt.Tooltip('Category:N', title='Category'),
            alt.Tooltip('Year:N', title='Period'),
            alt.Tooltip('Value_Billion_USD:Q', title='Value (Billion USD)', format=',.2f'),
            alt.Tooltip('YoY_Text:N', title='YoY Change')
        ]
    ).properties(
        title={
            "text": "Thailand's Top 5 Exports Comparative Analysis",
            "subtitle": "Comparison of Cumulative Exports (January – February) in 2025 vs. 2026",
            "fontSize": 18,
            "subtitleFontSize": 14,
            "anchor": "start",
            "color": "#0f172a"
        },
        width=550,
        height=350
    )
    
    # Add text labels on top of the bars to show values and YoY percentages
    text_labels = chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-4,
        fontSize=10,
        fontWeight='bold'
    ).encode(
        text=alt.Text('Value_Billion_USD:Q', format='.2f')
    )
    
    # Combine bars and text
    final_chart = alt.layer(chart, text_labels).configure_view(
        stroke=None
    ).configure_axis(
        grid=True,
        gridOpacity=0.4
    )
    
    # Save chart
    save_chart(final_chart, 'output/chart/thailand_top5_exports_comparison.png', save_html=True)
    print("Successfully generated and saved chart!")

if __name__ == '__main__':
    generate_grouped_bar_chart()

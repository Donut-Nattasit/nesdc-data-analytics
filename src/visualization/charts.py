import altair as alt
import vl_convert as vlc
import os
import pandas as pd
from typing import List, Tuple, Optional, Union

# Configure local font registration
FONTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "fonts"))
if os.path.exists(FONTS_DIR):
    try:
        # Register all font directories within assets/fonts
        for root, dirs, files in os.walk(FONTS_DIR):
            if any(f.endswith(('.ttf', '.otf')) for f in files):
                vlc.register_font_directory(root)
    except Exception as e:
        print(f"Warning: Could not register local fonts: {e}")

# Configure THSarabunNew as the default font
def th_sarabun_theme():
    font = "TH Sarabun New"
    return {
        "config": {
            "title": {"font": font, "fontSize": 18},
            "axis": {
                "labelFont": font,
                "titleFont": font,
                "labelFontSize": 14,
                "titleFontSize": 16
            },
            "header": {"labelFont": font, "titleFont": font},
            "legend": {
                "labelFont": font,
                "titleFont": font,
                "labelFontSize": 14,
                "titleFontSize": 16
            },
            "text": {"font": font}
        }
    }

alt.themes.register("thai_report", th_sarabun_theme)
alt.themes.enable("thai_report")

def get_standard_recession_periods() -> List[Tuple[str, str]]:
    """Return standard historical economic crisis spans for shading."""
    return [
        ('1997-07-02', '1998-12-31'),  # Asian Financial Crisis (Tom Yum Goong)
        ('2008-09-15', '2009-06-30'),  # Global Financial Crisis (Lehman Collapse)
        ('2020-03-01', '2021-06-30')   # COVID-19 Pandemic Shock
    ]

def create_recession_shading(df_or_dates: Union[pd.DataFrame, List[Tuple[str, str]]] = None) -> alt.Chart:
    """
    Create a layered background representing vertical recession shading.
    """
    if df_or_dates is None:
        periods = get_standard_recession_periods()
    elif isinstance(df_or_dates, list):
        periods = df_or_dates
    else:
        periods = get_standard_recession_periods()
        try:
            # Find the date column in the DataFrame
            date_col = None
            for col in df_or_dates.columns:
                if 'date' in col.lower() or pd.api.types.is_datetime64_any_dtype(df_or_dates[col]):
                    date_col = col
                    break
            
            if date_col is not None:
                # Convert the date column to datetime
                df_dates = pd.to_datetime(df_or_dates[date_col])
                min_date = df_dates.min()
                max_date = df_dates.max()
                
                # Filter periods that overlap with [min_date, max_date]
                filtered_periods = []
                for start, end in periods:
                    p_start = pd.to_datetime(start)
                    p_end = pd.to_datetime(end)
                    if not (p_end < min_date or p_start > max_date):
                        filtered_periods.append((start, end))
                
                if filtered_periods:
                    periods = filtered_periods
        except Exception as e:
            print(f"Warning: Failed to filter recession periods: {e}")

        
    shading_data = [{'start': p[0], 'end': p[1]} for p in periods]
    df_shading = pd.DataFrame(shading_data)
    df_shading['start'] = pd.to_datetime(df_shading['start'])
    df_shading['end'] = pd.to_datetime(df_shading['end'])
    
    shading_chart = alt.Chart(df_shading).mark_rect(
        opacity=0.15,
        color='gray'
    ).encode(
        x='start:T',
        x2='end:T'
    )
    return shading_chart

def create_line_chart(df: pd.DataFrame, x: str = 'date:T', y: str = 'value:Q', color: str = 'series_name:N', title: str = "Data Visualization", add_recessions: bool = False, interactive: bool = False) -> alt.Chart:
    """Create a standard Altair line chart (static by default), optionally with recession shading."""
    base_chart = alt.Chart(df).mark_line().encode(
        x=alt.X(x, title='Date'),
        y=alt.Y(y, title='Value', scale=alt.Scale(zero=False)),
        color=alt.Color(color, title='Series'),
        tooltip=[x, y, color]
    ).properties(
        title=title,
        width=800,
        height=400
    )
    
    if interactive:
        base_chart = base_chart.interactive()
    
    if add_recessions:
        shading = create_recession_shading(df)
        # Combine layered charts
        return alt.layer(shading, base_chart).properties(title=title)
        
    return base_chart

def create_horizontal_bar_chart(df: pd.DataFrame, x: str, y: str, title: str, color_scheme: str = 'viridis', width: int = 600, height: int = 300) -> alt.Chart:
    """Create a standard Altair horizontal bar chart."""
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(f'{x}:Q', title=x.replace('_', ' ')),
        y=alt.Y(f'{y}:N', sort='-x', title=y.replace('_', ' ')),
        color=alt.Color(f'{x}:Q', scale=alt.Scale(scheme=color_scheme), legend=None),
        tooltip=list(df.columns)
    ).properties(
        title=title,
        width=width,
        height=height
    )
    return chart

def create_dual_axis_chart(df: pd.DataFrame, x_col: str, y1_col: str, y2_col: str, y1_title: str, y2_title: str, title: str = "Dual-Axis Comparison", add_recessions: bool = False) -> alt.Chart:
    """
    Create a clean dual-axis line chart layered together.
    Useful for comparing growth rates against monetary rates or prices.
    """
    base = alt.Chart(df).encode(
        x=alt.X(x_col, title='Date')
    )
    
    line1 = base.mark_line(color='#1f77b4').encode(
        y=alt.Y(y1_col, title=y1_title, axis=alt.Axis(titleColor='#1f77b4'), scale=alt.Scale(zero=False)),
        tooltip=[x_col, y1_col]
    )
    
    line2 = base.mark_line(color='#ff7f0e').encode(
        y=alt.Y(y2_col, title=y2_title, axis=alt.Axis(titleColor='#ff7f0e'), scale=alt.Scale(zero=False)),
        tooltip=[x_col, y2_col]
    )
    
    # Layer and independent resolve
    layered = alt.layer(line1, line2).resolve_scale(
        y='independent'
    ).properties(
        title=title,
        width=800,
        height=400
    )
    
    if add_recessions:
        shading = create_recession_shading(df)
        return alt.layer(shading, layered).properties(title=title)
        
    return layered

def create_composition_chart(df: pd.DataFrame, x: str, y: str, color: str, title: str = "Composition Analysis", relative: bool = False, interactive: bool = False) -> alt.Chart:
    """
    Create a stacked area chart to analyze structural composition (static by default).
    """
    stack_type = 'normalize' if relative else 'zero'
    y_title = "Percentage Share (%)" if relative else "Absolute Value"
    
    chart = alt.Chart(df).mark_area(opacity=0.85).encode(
        x=alt.X(x, title='Date'),
        y=alt.Y(y, stack=stack_type, title=y_title),
        color=alt.Color(color, scale=alt.Scale(scheme='category20'), title='Component'),
        tooltip=[x, y, color]
    ).properties(
        title=title,
        width=800,
        height=400
    )
    
    if interactive:
        chart = chart.interactive()
    
    return chart

def save_chart(chart, filename: str, save_html: bool = False) -> Optional[str]:
    """
    Save Altair chart as static PNG, and optionally interactive HTML.
    All saving operations are relative to the project root and conform
    to the 'output/chart/' standard layout.
    """
    if not filename.endswith('.png'):
        filename += '.png'
    
    # Ensure correct standard output pathing (output/chart/)
    if filename.startswith('output' + os.sep) or filename.startswith('output/'):
        path = filename
    elif filename.startswith('chart' + os.sep) or filename.startswith('chart/'):
        # Map chart/... to output/chart/...
        path = os.path.join('output', filename)
    else:
        path = os.path.join('output', 'chart', filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    try:
        # Save static PNG
        png_data = vlc.vegalite_to_png(chart.to_json())
        with open(path, 'wb') as f:
            f.write(png_data)
        print(f"Chart saved to PNG: {path}")
        
        # Save interactive HTML
        if save_html:
            html_path = path.replace('.png', '.html')
            # Create html subfolder if needed
            html_dir = os.path.join(os.path.dirname(path), 'html')
            os.makedirs(html_dir, exist_ok=True)
            html_final_path = os.path.join(html_dir, os.path.basename(html_path))
            
            # Save chart as HTML using Altair standard save method
            chart.save(html_final_path)
            print(f"Interactive HTML saved: {html_final_path}")
            
        return path
    except Exception as e:
        print(f"Failed to save chart: {e}")
        return None

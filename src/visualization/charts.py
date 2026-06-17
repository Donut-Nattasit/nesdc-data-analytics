import altair as alt
import vl_convert as vlc
import os
import pandas as pd
from typing import List, Tuple, Optional, Union
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.figure
from matplotlib import font_manager
import textwrap

# Configure local font registration
FONTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "fonts"))
if os.path.exists(FONTS_DIR):
    try:
        # Register all font directories within assets/fonts
        for root, dirs, files in os.walk(FONTS_DIR):
            if any(f.endswith(('.ttf', '.otf')) for f in files):
                vlc.register_font_directory(root)
    except Exception as e:
        print(f"Warning: Could not register local fonts for vl-convert: {e}")

# Path to the NESDC style sheet (same directory as this file)
_STYLE_PATH = os.path.join(os.path.dirname(__file__), "nesdc_style.mplstyle")

# Register font for matplotlib/seaborn fallback
def configure_matplotlib_font(font_name: str = 'FC Vision'):
    if os.path.exists(FONTS_DIR):
        try:
            for root, dirs, files in os.walk(FONTS_DIR):
                for f in files:
                    if f.endswith(('.ttf', '.otf')):
                        font_path = os.path.join(root, f)
                        try:
                            font_manager.fontManager.addfont(font_path)
                        except Exception:
                            pass
            # Apply NESDC brand style sheet first, then set font family on top
            if os.path.exists(_STYLE_PATH):
                plt.style.use(_STYLE_PATH)
            plt.rcParams['font.family'] = font_name
        except Exception as e:
            print(f"Warning: Could not configure matplotlib style: {e}")

# Configure FCVision as the default font with bottom legends for Altair (when requested)
def fc_vision_theme():
    font = "FC Vision"
    return {
        "config": {
            "title": {"font": font, "fontSize": 18, "anchor": "middle", "fontWeight": "bold"},
            "axis": {
                "labelFont": font,
                "titleFont": font,
                "labelFontSize": 12,
                "titleFontSize": 14
            },
            "header": {"labelFont": font, "titleFont": font},
            "legend": {
                "orient": "bottom",
                "direction": "horizontal",
                "align": "center",
                "labelFont": font,
                "titleFont": font,
                "labelFontSize": 11,
                "titleFontSize": 12,
                "padding": 15
            },
            "text": {"font": font}
        }
    }

# Configure THSarabunNew as an optional localized font for Altair (when requested)
def th_sarabun_theme():
    font = "TH Sarabun New"
    return {
        "config": {
            "title": {"font": font, "fontSize": 18, "fontWeight": "bold"},
            "axis": {
                "labelFont": font,
                "titleFont": font,
                "labelFontSize": 14,
                "titleFontSize": 16
            },
            "header": {"labelFont": font, "titleFont": font},
            "legend": {
                "orient": "bottom",
                "direction": "horizontal",
                "align": "center",
                "labelFont": font,
                "titleFont": font,
                "labelFontSize": 14,
                "titleFontSize": 16,
                "padding": 15
            },
            "text": {"font": font}
        }
    }

alt.themes.register("fc_vision_theme", fc_vision_theme)
alt.themes.register("thai_report", th_sarabun_theme)
alt.themes.enable("fc_vision_theme")

def get_standard_recession_periods() -> List[Tuple[str, str]]:
    """Return standard historical economic crisis spans for shading."""
    return [
        ('1997-07-02', '1998-12-31'),  # Asian Financial Crisis (Tom Yum Goong)
        ('2008-09-15', '2009-06-30'),  # Global Financial Crisis (Lehman Collapse)
        ('2020-03-01', '2021-06-30')   # COVID-19 Pandemic Shock
    ]

def create_recession_shading(df_or_dates: Union[pd.DataFrame, List[Tuple[str, str]]] = None) -> alt.Chart:
    """
    Create a layered background representing vertical recession shading in Altair.
    """
    if df_or_dates is None:
        periods = get_standard_recession_periods()
    elif isinstance(df_or_dates, list):
        periods = df_or_dates
    else:
        periods = get_standard_recession_periods()
        try:
            date_col = None
            for col in df_or_dates.columns:
                if 'date' in col.lower() or pd.api.types.is_datetime64_any_dtype(df_or_dates[col]):
                    date_col = col
                    break
            
            if date_col is not None:
                df_dates = pd.to_datetime(df_or_dates[date_col])
                min_date = df_dates.min()
                max_date = df_dates.max()
                
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

def create_line_chart(df: pd.DataFrame, x: str = 'date:T', y: str = 'value:Q', color: str = 'series_name:N', title: str = "Data Visualization", add_recessions: bool = False, interactive: bool = False, use_altair: bool = False, font_name: str = 'FC Vision', thai_locale: bool = False, subtitle: Optional[str] = None, source: Optional[str] = None) -> Union[alt.Chart, matplotlib.figure.Figure]:
    """Create a standard line chart. Seaborn/Matplotlib by default, Altair if use_altair=True or interactive=True."""
    clean_x = x.split(':')[0]
    clean_y = y.split(':')[0]
    clean_color = color.split(':')[0] if color else None
    
    if use_altair or interactive:
        # Altair Nominals (When explicitly requested)
        is_temp = ':T' in x
        if thai_locale:
            x_axis = alt.X(x, title=None if is_temp else 'วันที่', axis=alt.Axis(labelExpr="timeFormat(datum.value, '%Y')*1 + 543"))
            if 'oil' in title.lower() or 'น้ำมันดิบ' in title or 'ราคาน้ำมัน' in title:
                y_title = 'ดอลลาร์ สรอ. ต่อบาร์เรล'
            else:
                y_title = None
        else:
            x_axis = alt.X(x, title=None if is_temp else 'Date')
            y_title = None
            
        if subtitle and source:
            title_params = alt.TitleParams(text=title, subtitle=[subtitle, f"ที่มา: {source}" if thai_locale else f"Source: {source}"], anchor='middle')
        elif subtitle:
            title_params = alt.TitleParams(text=title, subtitle=subtitle, anchor='middle')
        elif source:
            title_params = alt.TitleParams(text=title, subtitle=f"ที่มา: {source}" if thai_locale else f"Source: {source}", anchor='middle')
        else:
            title_params = title

        base_chart = alt.Chart(df).mark_line().encode(
            x=x_axis,
            y=alt.Y(y, title=y_title, scale=alt.Scale(zero=False)),
            color=alt.Color(color, title='Series', legend=alt.Legend(orient='bottom', direction='horizontal', title=None)),
            tooltip=[x, y, color]
        ).properties(
            title=title_params,
            width=800,
            height=400
        )
        if interactive:
            base_chart = base_chart.interactive()
        if add_recessions:
            shading = create_recession_shading(df)
            return alt.layer(shading, base_chart).properties(title=title_params)
        return base_chart
        
    else:
        # Standard Default Seaborn Path
        configure_matplotlib_font(font_name)
        fig, ax = plt.subplots(figsize=(10, 5))
        
        is_temporal = ':T' in x or pd.api.types.is_datetime64_any_dtype(df[clean_x])
        plot_df = df.copy()
        if is_temporal:
            plot_df[clean_x] = pd.to_datetime(plot_df[clean_x])
            
        # Apply date formatting based on range and locale
        if is_temporal:
            import matplotlib.dates as mdates
            from matplotlib.ticker import FuncFormatter
            
            min_date = plot_df[clean_x].min()
            max_date = plot_df[clean_x].max()
            
            if not pd.isna(min_date) and not pd.isna(max_date):
                date_range = max_date - min_date
                
                # Less than 3 years -> Monthly formatting standard
                if date_range < pd.Timedelta(days=3 * 365):
                    if thai_locale:
                        thai_months = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
                        ax.xaxis.set_major_formatter(FuncFormatter(lambda val, pos: f"{thai_months[mdates.num2date(val).month - 1]} {mdates.num2date(val).year + 543}"))
                    else:
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
                else:
                    # Long-term -> Yearly formatting standard
                    if thai_locale:
                        ax.xaxis.set_major_formatter(FuncFormatter(lambda val, pos: f"{mdates.num2date(val).year + 543}"))
            
        # Official NESDC Solid Color Palette
        nesdc_palette = ["#00109E", "#78DED4", "#BFB997", "#60B1E7", "#FFA300"]
        
        if clean_color and clean_color in plot_df.columns:
            sns.lineplot(data=plot_df, x=clean_x, y=clean_y, hue=clean_color, ax=ax, palette=nesdc_palette[:len(plot_df[clean_color].unique())], linewidth=2.5)
        else:
            sns.lineplot(data=plot_df, x=clean_x, y=clean_y, ax=ax, color="#00109E", linewidth=2.5)

            
        if subtitle:
            fig.suptitle(title, fontsize=14, fontweight='bold', x=0.5, y=0.97, ha='center')
            ax.set_title(subtitle, fontsize=10, color='#64748b', pad=10, loc='center')
        else:
            ax.set_title(title, fontsize=14, fontweight='bold', pad=15, loc='center')
        
        # Remove X-axis label by default if it is a date/temporal column
        if is_temporal:
            ax.set_xlabel(None)
            ax.xaxis.label.set_visible(False)
        else:
            if thai_locale and clean_x.lower() == 'date':
                ax.set_xlabel("วันที่", fontsize=11, fontweight='medium')
            else:
                ax.set_xlabel(clean_x.replace('_', ' ').capitalize(), fontsize=11, fontweight='medium')
            
        # Localize Y-axis description if Thai locale requested
        if thai_locale:
            if clean_y == 'value' and ('oil' in title.lower() or 'น้ำมันดิบ' in title or 'ราคาน้ำมัน' in title):
                y_label = 'ดอลลาร์ สรอ. ต่อบาร์เรล'
            elif clean_y == 'value':
                y_label = None
            else:
                y_label = clean_y
        else:
            if clean_y.lower() == 'value':
                y_label = None
            else:
                y_label = clean_y.capitalize()
            
        if y_label:
            ax.set_ylabel(y_label, fontsize=11, fontweight='medium')
        else:
            ax.set_ylabel(None)
        
        if add_recessions:
            periods = get_standard_recession_periods()
            min_date = plot_df[clean_x].min()
            max_date = plot_df[clean_x].max()
            for start, end in periods:
                p_start = pd.to_datetime(start)
                p_end = pd.to_datetime(end)
                if not (p_end < min_date or p_start > max_date):
                    ax.axvspan(p_start, p_end, color='gray', alpha=0.15)
                    
        # Center horizontal legend underneath the axis without redundant title
        if ax.get_legend():
            handles, labels = ax.get_legend_handles_labels()
            ncol = min(4, len(labels))
            if is_temporal:
                ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.06), ncol=ncol, frameon=True, title=None)
                plt.tight_layout()
                bottom_val = 0.14
            else:
                ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.18), ncol=ncol, frameon=True, title=None)
                plt.tight_layout()
                bottom_val = 0.22
        else:
            plt.tight_layout()
            bottom_val = 0.10 if is_temporal else 0.14
            
        if subtitle:
            fig.subplots_adjust(bottom=bottom_val, top=0.87)
        else:
            fig.subplots_adjust(bottom=bottom_val)
            
        if source:
            if thai_locale:
                prefix = "ที่มา: "
            else:
                prefix = "Source: "
            source_text = source if (source.startswith("Source:") or source.startswith("ที่มา:")) else f"{prefix}{source}"
            fig.text(0.08, 0.02, source_text, fontsize=9, color='#64748b', ha='left', family=font_name)
            
        return fig

def create_horizontal_bar_chart(df: pd.DataFrame, x: str, y: str, title: str, color_scheme: str = 'viridis', width: int = 600, height: int = 300, use_altair: bool = False, font_name: str = 'FC Vision', thai_locale: bool = False, subtitle: Optional[str] = None, source: Optional[str] = None) -> Union[alt.Chart, matplotlib.figure.Figure]:
    """Create a standard horizontal bar chart. Seaborn/Matplotlib by default, Altair if use_altair=True."""
    clean_x = x.split(':')[0]
    clean_y = y.split(':')[0]
    
    if use_altair:
        # Altair Nominals (When explicitly requested)
        x_title = 'วันที่' if (thai_locale and clean_x.lower() == 'date') else x.replace('_', ' ')
        y_title = 'วันที่' if (thai_locale and clean_y.lower() == 'date') else y.replace('_', ' ')
        if subtitle and source:
            title_params = alt.TitleParams(text=title, subtitle=[subtitle, f"ที่มา: {source}" if thai_locale else f"Source: {source}"], anchor='middle')
        elif subtitle:
            title_params = alt.TitleParams(text=title, subtitle=subtitle, anchor='middle')
        elif source:
            title_params = alt.TitleParams(text=title, subtitle=f"ที่มา: {source}" if thai_locale else f"Source: {source}", anchor='middle')
        else:
            title_params = title

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(f'{x}:Q', title=x_title),
            y=alt.Y(f'{y}:N', sort='-x', title=y_title),
            color=alt.Color(f'{x}:Q', scale=alt.Scale(scheme=color_scheme), legend=None),
            tooltip=list(df.columns)
        ).properties(
            title=title_params,
            width=width,
            height=height
        )
        return chart
        
    else:
        # Standard Default Seaborn Path
        configure_matplotlib_font(font_name)
        fig, ax = plt.subplots(figsize=(width/80, height/80))
        
        plot_df = df.sort_values(by=clean_x, ascending=False).copy()
        # Strictly use NESDC brand colors for up to 5 categories, fallback to brand-consistent Blues gradient
        nesdc_palette = ["#00109E", "#78DED4", "#BFB997", "#60B1E7", "#FFA300"]
        num_categories = len(plot_df[clean_y].unique())
        if num_categories <= len(nesdc_palette):
            palette = nesdc_palette[:num_categories]
        else:
            palette = sns.color_palette("Blues_r", n_colors=num_categories)
        sns.barplot(data=plot_df, x=clean_x, y=clean_y, ax=ax, palette=palette)
        
        if subtitle:
            fig.suptitle(title, fontsize=14, fontweight='bold', x=0.5, y=0.97, ha='center')
            ax.set_title(subtitle, fontsize=10, color='#64748b', pad=10, loc='center')
            plt.tight_layout()
            fig.subplots_adjust(top=0.87)
        else:
            ax.set_title(title, fontsize=14, fontweight='bold', pad=15, loc='center')
            plt.tight_layout()
        
        # Check if we should translate date to วันที่
        if thai_locale and clean_x.lower() == 'date':
            ax.set_xlabel("วันที่", fontsize=11)
        elif clean_x.lower() == 'value' or clean_x == 'ค่า':
            ax.set_xlabel(None)
        else:
            ax.set_xlabel(clean_x.replace('_', ' ').capitalize(), fontsize=11)
            
        if thai_locale and clean_y.lower() == 'date':
            ax.set_ylabel("วันที่", fontsize=11)
        elif clean_y.lower() == 'value' or clean_y == 'ค่า':
            ax.set_ylabel(None)
        else:
            ax.set_ylabel(clean_y.replace('_', ' ').capitalize(), fontsize=11)
        
        plt.tight_layout()
        if source:
            if thai_locale:
                prefix = "ที่มา: "
            else:
                prefix = "Source: "
            source_text = source if (source.startswith("Source:") or source.startswith("ที่มา:")) else f"{prefix}{source}"
            fig.text(0.08, 0.02, source_text, fontsize=9, color='#64748b', ha='left', family=font_name)
        return fig

def create_dual_axis_chart(df: pd.DataFrame, x_col: str, y1_col: str, y2_col: str, y1_title: str, y2_title: str, title: str = "Dual-Axis Comparison", add_recessions: bool = False, use_altair: bool = False, font_name: str = 'FC Vision', thai_locale: bool = False, subtitle: Optional[str] = None, source: Optional[str] = None) -> Union[alt.Chart, matplotlib.figure.Figure]:
    """Create a dual-axis line chart. Seaborn/Matplotlib by default, Altair if use_altair=True."""
    clean_x = x_col.split(':')[0]
    clean_y1 = y1_col.split(':')[0]
    clean_y2 = y2_col.split(':')[0]
    
    if use_altair:
        # Altair Nominals (When explicitly requested)
        is_temp = ':T' in x_col
        x_title = None if is_temp else ('วันที่' if thai_locale else 'Date')
        base = alt.Chart(df).encode(
            x=alt.X(x_col, title=x_title)
        )
        line1 = base.mark_line(color='#1f77b4').encode(
            y=alt.Y(y1_col, title=y1_title, axis=alt.Axis(titleColor='#1f77b4'), scale=alt.Scale(zero=False)),
            tooltip=[x_col, y1_col]
        )
        line2 = base.mark_line(color='#ff7f0e').encode(
            y=alt.Y(y2_col, title=y2_title, axis=alt.Axis(titleColor='#ff7f0e'), scale=alt.Scale(zero=False)),
            tooltip=[x_col, y2_col]
        )
        if subtitle and source:
            title_params = alt.TitleParams(text=title, subtitle=[subtitle, f"ที่มา: {source}" if thai_locale else f"Source: {source}"], anchor='middle')
        elif subtitle:
            title_params = alt.TitleParams(text=title, subtitle=subtitle, anchor='middle')
        elif source:
            title_params = alt.TitleParams(text=title, subtitle=f"ที่มา: {source}" if thai_locale else f"Source: {source}", anchor='middle')
        else:
            title_params = title

        layered = alt.layer(line1, line2).resolve_scale(
            y='independent'
        ).properties(
            title=title_params,
            width=800,
            height=400
        )
        if add_recessions:
            shading = create_recession_shading(df)
            return alt.layer(shading, layered).properties(title=title_params)
        return layered
        
    else:
        # Standard Default Seaborn Path
        configure_matplotlib_font(font_name)
        fig, ax1 = plt.subplots(figsize=(10, 5))
        
        is_temporal = ':T' in x_col or pd.api.types.is_datetime64_any_dtype(df[clean_x])
        plot_df = df.copy()
        if is_temporal:
            plot_df[clean_x] = pd.to_datetime(plot_df[clean_x])
            
        # Apply Thai Calendar Year Skill (BE = CE + 543)
        if thai_locale and is_temporal:
            import matplotlib.dates as mdates
            from matplotlib.ticker import FuncFormatter
            ax1.xaxis.set_major_formatter(FuncFormatter(lambda val, pos: f"{mdates.num2date(val).year + 543}"))
        if is_temporal:
            plot_df[clean_x] = pd.to_datetime(plot_df[clean_x])
            
        color1 = '#00109E'  # Sapphire Blue
        sns.lineplot(data=plot_df, x=clean_x, y=clean_y1, ax=ax1, color=color1, linewidth=2.5)
        if subtitle:
            fig.suptitle(title, fontsize=14, fontweight='bold', x=0.5, y=0.97, ha='center')
            ax1.set_title(subtitle, fontsize=10, color='#64748b', pad=10, loc='center')
        else:
            ax1.set_title(title, fontsize=14, fontweight='bold', pad=15, loc='center')
        
        # Remove X-axis label by default if it is a date/temporal column
        if is_temporal:
            ax1.set_xlabel(None)
            ax1.xaxis.label.set_visible(False)
        else:
            if thai_locale and clean_x.lower() == 'date':
                ax1.set_xlabel("วันที่", fontsize=11, fontweight='medium')
            else:
                ax1.set_xlabel(clean_x.replace('_', ' ').capitalize(), fontsize=11, fontweight='medium')
            
        y1_label = None if y1_title.lower() in ['value', 'ค่า'] else y1_title
        if y1_label:
            ax1.set_ylabel(y1_label, color=color1, fontsize=11, fontweight='medium')
        else:
            ax1.set_ylabel(None)
        ax1.tick_params(axis='y', labelcolor=color1)
        
        ax2 = ax1.twinx()
        color2 = '#FFA300'  # Saffron support color
        sns.lineplot(data=plot_df, x=clean_x, y=clean_y2, ax=ax2, color=color2, linewidth=2.5)
        y2_label = None if y2_title.lower() in ['value', 'ค่า'] else y2_title
        if y2_label:
            ax2.set_ylabel(y2_label, color=color2, fontsize=11, fontweight='medium')
        else:
            ax2.set_ylabel(None)
        ax2.tick_params(axis='y', labelcolor=color2)

        
        if add_recessions:
            periods = get_standard_recession_periods()
            min_date = plot_df[clean_x].min()
            max_date = plot_df[clean_x].max()
            for start, end in periods:
                p_start = pd.to_datetime(start)
                p_end = pd.to_datetime(end)
                if not (p_end < min_date or p_start > max_date):
                    ax1.axvspan(p_start, p_end, color='gray', alpha=0.15)
                    
        # Centered horizontal bottom legends with no title
        lines = ax1.get_lines() + ax2.get_lines()
        labels = [y1_title, y2_title]
        if is_temporal:
            ax1.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.5, -0.06), ncol=2, frameon=True, title=None)
            plt.tight_layout()
            bottom_val = 0.14
        else:
            ax1.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.5, -0.18), ncol=2, frameon=True, title=None)
            plt.tight_layout()
            bottom_val = 0.22
            
        if subtitle:
            fig.subplots_adjust(bottom=bottom_val, top=0.87)
        else:
            fig.subplots_adjust(bottom=bottom_val)
            
        if source:
            if thai_locale:
                prefix = "ที่มา: "
            else:
                prefix = "Source: "
            source_text = source if (source.startswith("Source:") or source.startswith("ที่มา:")) else f"{prefix}{source}"
            fig.text(0.08, 0.02, source_text, fontsize=9, color='#64748b', ha='left', family=font_name)
            
        return fig

def create_composition_chart(df: pd.DataFrame, x: str, y: str, color: str, title: str = "Composition Analysis", relative: bool = False, interactive: bool = False, use_altair: bool = False, font_name: str = 'FC Vision', thai_locale: bool = False, subtitle: Optional[str] = None, source: Optional[str] = None) -> Union[alt.Chart, matplotlib.figure.Figure]:
    """Create a stacked area composition chart. Seaborn/Matplotlib by default, Altair if use_altair=True or interactive=True."""
    clean_x = x.split(':')[0]
    clean_y = y.split(':')[0]
    clean_color = color.split(':')[0]
    
    if use_altair or interactive:
        # Altair Nominals (When explicitly requested)
        stack_type = 'normalize' if relative else 'zero'
        y_title = "Percentage Share (%)" if relative else "Absolute Value"
        is_temp = ':T' in x
        
        if thai_locale:
            x_axis = alt.X(x, title=None if is_temp else 'วันที่', axis=alt.Axis(labelExpr="timeFormat(datum.value, '%Y')*1 + 543"))
        else:
            x_axis = alt.X(x, title=None if is_temp else 'Date')
            
        if subtitle and source:
            title_params = alt.TitleParams(text=title, subtitle=[subtitle, f"ที่มา: {source}" if thai_locale else f"Source: {source}"], anchor='middle')
        elif subtitle:
            title_params = alt.TitleParams(text=title, subtitle=subtitle, anchor='middle')
        elif source:
            title_params = alt.TitleParams(text=title, subtitle=f"ที่มา: {source}" if thai_locale else f"Source: {source}", anchor='middle')
        else:
            title_params = title

        chart = alt.Chart(df).mark_area(opacity=0.85).encode(
            x=x_axis,
            y=alt.Y(y, stack=stack_type, title=y_title),
            color=alt.Color(color, scale=alt.Scale(scheme='category20'), title='Component', legend=alt.Legend(orient='bottom', direction='horizontal', title=None)),
            tooltip=[x, y, color]
        ).properties(
            title=title_params,
            width=800,
            height=400
        )
        if interactive:
            chart = chart.interactive()
        return chart
        
    else:
        # Standard Default Matplotlib Stackplot Path
        configure_matplotlib_font(font_name)
        fig, ax = plt.subplots(figsize=(10, 5))
        
        is_temporal = ':T' in x or pd.api.types.is_datetime64_any_dtype(df[clean_x])
        plot_df = df.copy()
        if is_temporal:
            plot_df[clean_x] = pd.to_datetime(plot_df[clean_x])
            
        # Apply Thai Calendar Year Skill (BE = CE + 543)
        if thai_locale and is_temporal:
            import matplotlib.dates as mdates
            from matplotlib.ticker import FuncFormatter
            ax.xaxis.set_major_formatter(FuncFormatter(lambda val, pos: f"{mdates.num2date(val).year + 543}"))
        if is_temporal:
            plot_df[clean_x] = pd.to_datetime(plot_df[clean_x])
            
        pivot_df = plot_df.pivot(index=clean_x, columns=clean_color, values=clean_y).fillna(0)
        
        if relative:
            pivot_df = pivot_df.div(pivot_df.sum(axis=1), axis=0) * 100
            y_title = "Percentage Share (%)"
        else:
            y_title = "Absolute Value"
            
        # Strictly use NESDC brand colors for stackplot
        nesdc_palette = ["#00109E", "#78DED4", "#BFB997", "#60B1E7", "#FFA300"]
        colors = nesdc_palette[:len(pivot_df.columns)]
        ax.stackplot(pivot_df.index, [pivot_df[col] for col in pivot_df.columns], labels=pivot_df.columns, colors=colors, alpha=0.85)
        
        if subtitle:
            fig.suptitle(title, fontsize=14, fontweight='bold', x=0.5, y=0.97, ha='center')
            ax.set_title(subtitle, fontsize=10, color='#64748b', pad=10, loc='center')
        else:
            ax.set_title(title, fontsize=14, fontweight='bold', pad=15, loc='center')
        
        # Remove X-axis label by default if it is a date/temporal column
        if is_temporal:
            ax.set_xlabel(None)
            ax.xaxis.label.set_visible(False)
        else:
            if thai_locale and clean_x.lower() == 'date':
                ax.set_xlabel("วันที่", fontsize=11, fontweight='medium')
            else:
                ax.set_xlabel(clean_x.replace('_', ' ').capitalize(), fontsize=11, fontweight='medium')
            
        if y_title and y_title.lower() not in ['value', 'ค่า']:
            ax.set_ylabel(y_title, fontsize=11)
        else:
            ax.set_ylabel(None)
        
        ncol = min(4, len(pivot_df.columns))
        if is_temporal:
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.06), ncol=ncol, frameon=True, title=None)
            plt.tight_layout()
            bottom_val = 0.14
        else:
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.18), ncol=ncol, frameon=True, title=None)
            plt.tight_layout()
            bottom_val = 0.22
            
        if subtitle:
            fig.subplots_adjust(bottom=bottom_val, top=0.87)
        else:
            fig.subplots_adjust(bottom=bottom_val)
            
        if source:
            if thai_locale:
                prefix = "ที่มา: "
            else:
                prefix = "Source: "
            source_text = source if (source.startswith("Source:") or source.startswith("ที่มา:")) else f"{prefix}{source}"
            fig.text(0.08, 0.02, source_text, fontsize=9, color='#64748b', ha='left', family=font_name)
            
        return fig

def create_fan_chart(
    df: pd.DataFrame,
    date_col: str,
    forecast_col: str,
    actual_col: Optional[str] = None,
    ci_80_lower: Optional[str] = None,
    ci_80_upper: Optional[str] = None,
    ci_95_lower: Optional[str] = None,
    ci_95_upper: Optional[str] = None,
    title: str = "Forecast with Confidence Intervals",
    y_label: Optional[str] = None,
    forecast_start: Optional[str] = None,
    font_name: str = 'FC Vision',
    thai_locale: bool = False,
    subtitle: Optional[str] = None,
    source: Optional[str] = None,
) -> matplotlib.figure.Figure:
    """
    Fan chart for economic forecasts with shaded confidence intervals.
    - Solid line  : historical actuals (Sapphire Blue)
    - Dashed line : point forecast (Sapphire Blue)
    - Dark band   : 80% confidence interval
    - Light band  : 95% confidence interval
    - Dotted line : forecast start marker (Clay)
    """
    configure_matplotlib_font(font_name)
    fig, ax = plt.subplots(figsize=(10, 5.2))

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    if df[forecast_col].isna().any():
        nan_count = df[forecast_col].isna().sum()
        print(f"[WARN] {nan_count} NaN values in '{forecast_col}' — chart will show gaps. Inspect data pipeline.")

    # 95% CI — lightest band
    if ci_95_lower and ci_95_upper and ci_95_lower in df.columns and ci_95_upper in df.columns:
        ax.fill_between(df[date_col], df[ci_95_lower], df[ci_95_upper],
                        alpha=0.12, color='#00109E', label='95% CI')

    # 80% CI — darker band
    if ci_80_lower and ci_80_upper and ci_80_lower in df.columns and ci_80_upper in df.columns:
        ax.fill_between(df[date_col], df[ci_80_lower], df[ci_80_upper],
                        alpha=0.28, color='#00109E', label='80% CI')

    # Point forecast — dashed
    mask_fc = df[forecast_col].notna()
    ax.plot(df.loc[mask_fc, date_col], df.loc[mask_fc, forecast_col],
            color='#00109E', linewidth=2.5, linestyle='--', label='Forecast')

    # Historical actuals — solid
    if actual_col and actual_col in df.columns:
        mask_act = df[actual_col].notna()
        ax.plot(df.loc[mask_act, date_col], df.loc[mask_act, actual_col],
                color='#00109E', linewidth=2.5, linestyle='-', label='Actual')

    # Forecast start vertical marker
    if forecast_start:
        ax.axvline(pd.to_datetime(forecast_start), color='#BFB997',
                   linewidth=1.2, linestyle=':', alpha=0.9)

    # Date formatting
    import matplotlib.dates as mdates
    from matplotlib.ticker import FuncFormatter
    date_range = df[date_col].max() - df[date_col].min()
    if date_range < pd.Timedelta(days=3 * 365):
        if thai_locale:
            thai_months = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
                           "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
            ax.xaxis.set_major_formatter(FuncFormatter(
                lambda val, pos: f"{thai_months[mdates.num2date(val).month - 1]} {mdates.num2date(val).year + 543}"
            ))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    else:
        if thai_locale:
            ax.xaxis.set_major_formatter(FuncFormatter(
                lambda val, pos: str(mdates.num2date(val).year + 543)
            ))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    ax.set_xlabel(None)
    if y_label:
        ax.set_ylabel(y_label, fontsize=11, fontweight='medium')
    else:
        ax.set_ylabel(None)

    if subtitle:
        fig.suptitle(title, fontsize=14, fontweight='bold', x=0.5, y=0.97, ha='center')
        ax.set_title(subtitle, fontsize=10, color='#64748b', pad=10, loc='center')
    else:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15, loc='center')

    handles, labels = ax.get_legend_handles_labels()
    ncol = min(4, len(labels))
    ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.06),
              ncol=ncol, frameon=True, title=None)

    bottom_val = 0.14
    if subtitle:
        fig.subplots_adjust(bottom=bottom_val, top=0.87)
    else:
        fig.subplots_adjust(bottom=bottom_val)

    if source:
        prefix = "ที่มา: " if thai_locale else "Source: "
        source_text = source if source.startswith(("Source:", "ที่มา:")) else f"{prefix}{source}"
        fig.text(0.08, 0.02, source_text, fontsize=9, color='#64748b', ha='left', family=font_name)

    return fig


def save_chart(chart, filename: str, save_html: bool = False) -> Optional[str]:
    """
    Save Altair chart as static PNG, and optionally interactive HTML.
    Supports native Matplotlib Figure object saving as well.
    """
    if not filename.endswith('.png'):
        filename += '.png'
    
    # Ensure correct standard output pathing (output/chart/)
    if filename.startswith('output' + os.sep) or filename.startswith('output/'):
        path = filename
    elif filename.startswith('chart' + os.sep) or filename.startswith('chart/'):
        path = os.path.join('output', filename)
    else:
        path = os.path.join('output', 'chart', filename)
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    try:
        # Check if the chart is a Matplotlib Figure (Default Path)
        if isinstance(chart, (plt.Figure, matplotlib.figure.Figure)):
            # Apply safe native optimization (reduced DPI and PIL optimization)
            chart.savefig(path, bbox_inches='tight', dpi=300, pil_kwargs={'optimize': True})
            plt.close(chart)
            print(f"[Save Success] Seaborn/Matplotlib chart successfully saved to PNG: {path}")
            return path
            
        # Altair Saving via vl-convert
        png_data = vlc.vegalite_to_png(chart.to_json())
        with open(path, 'wb') as f:
            f.write(png_data)
        print(f"[Save Success] Altair chart successfully saved to PNG: {path}")
        
        # Save interactive HTML (Only if explicitly requested)
        if save_html:
            html_path = path.replace('.png', '.html')
            chart.save(html_path)
            print(f"[Save Success] Interactive HTML saved to: {html_path}")
            
        return path
    except Exception as e:
        print(f"[Save Error] Failed to save chart: {e}")
        return None

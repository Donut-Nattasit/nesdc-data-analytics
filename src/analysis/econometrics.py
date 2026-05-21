import os
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.x13 import x13_arima_analysis

def seasonal_adjustment(series, freq='QS'):
    """
    Perform X13-ARIMA-SEATS seasonal adjustment.
    Requires bin/x13as.exe.
    """
    series = series.resample(freq).last()
    x12path = os.path.abspath("bin")
    try:
        results = x13_arima_analysis(series, x12path=x12path)
        return results.seasadj
    except Exception as e:
        print(f"Seasonal adjustment failed: {e}")
        return None

def calculate_growth(df, type='yoy', date_col='date', value_col='value', group_col='series_id'):
    """Calculate YoY, QoQ, or MoM growth rates."""
    df = df.copy().sort_values([group_col, date_col])
    first_group = df[df[group_col] == df[group_col].iloc[0]]
    if len(first_group) < 2:
        return df
    
    diff = (first_group[date_col].iloc[1] - first_group[date_col].iloc[0]).days
    periods = 1
    if 25 <= diff <= 32: # Monthly
        periods = 12 if type == 'yoy' else 1
    elif 85 <= diff <= 95: # Quarterly
        periods = 4 if type == 'yoy' else 1
    elif diff < 5: # Daily
        periods = 365 if type == 'yoy' else 1
        
    df['growth'] = df.groupby(group_col)[value_col].pct_change(periods=periods) * 100
    return df

def rebase(series, base_date):
    """Rebase a series to a specific date = 100."""
    base_val = series.asof(pd.to_datetime(base_date))
    if base_val and base_val != 0:
        return (series / base_val) * 100
    return series

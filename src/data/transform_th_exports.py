import pandas as pd
from pathlib import Path

def transform_exports():
    project_root = Path.cwd()
    raw_path = project_root / 'output/data/raw' / 'thailand_top5_exports_raw.csv'
    transformed_dir = project_root / 'output/data/transformed'
    transformed_dir.mkdir(parents=True, exist_ok=True)
    growth_output_path = transformed_dir / 'thailand_top5_exports_growth.csv'
    monthly_output_path = transformed_dir / 'thailand_top5_exports_monthly.csv'
    
    # Load raw data
    df = pd.read_csv(raw_path)
    
    # 1. Aggregate partner-level data to total monthly exports by HS2 Code
    # Group by Year, Month, HS2_Code, and Description and sum USD
    monthly_agg = df.groupby(['Year', 'Month', 'HS2_Code', 'HS2_Desc_EN'])['USD'].sum().reset_index()
    monthly_agg.to_csv(monthly_output_path, index=False, encoding='utf-8')
    print(f"Aggregated monthly export data saved to {monthly_output_path}")
    
    # 2. Identify available months in 2026
    df_2026 = monthly_agg[monthly_agg['Year'] == 2026]
    available_months_2026 = sorted(df_2026['Month'].unique())
    print(f"Available months in 2026: {available_months_2026}")
    
    # 3. Compute period comparisons (YoY)
    # Get full year 2025 sum
    df_2025 = monthly_agg[monthly_agg['Year'] == 2025]
    val_2025_full = df_2025.groupby(['HS2_Code', 'HS2_Desc_EN'])['USD'].sum().reset_index(name='USD_2025_Full')
    
    # Get period sum for 2025
    df_2025_period = df_2025[df_2025['Month'].isin(available_months_2026)]
    val_2025_period = df_2025_period.groupby(['HS2_Code', 'HS2_Desc_EN'])['USD'].sum().reset_index(name='USD_2025_Period')
    
    # Get period sum for 2026
    df_2026_period = df_2026[df_2026['Month'].isin(available_months_2026)]
    val_2026_period = df_2026_period.groupby(['HS2_Code', 'HS2_Desc_EN'])['USD'].sum().reset_index(name='USD_2026_Period')
    
    # Merge datasets
    summary_df = pd.merge(val_2025_full, val_2025_period, on=['HS2_Code', 'HS2_Desc_EN'], how='left')
    summary_df = pd.merge(summary_df, val_2026_period, on=['HS2_Code', 'HS2_Desc_EN'], how='left')
    
    # Calculate YoY change
    summary_df['YoY_Change_Pct'] = ((summary_df['USD_2026_Period'] / summary_df['USD_2025_Period']) - 1) * 100
    
    # Save transformed summary
    summary_df.to_csv(growth_output_path, index=False, encoding='utf-8')
    print(f"Transformed comparison summary saved to {growth_output_path}")
    
    # Preview
    print("\nSummary Comparison Table:")
    print(summary_df.to_string(index=False))

if __name__ == '__main__':
    transform_exports()

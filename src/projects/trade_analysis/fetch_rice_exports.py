import os
import time
import pandas as pd
from pathlib import Path
from datetime import datetime
from src.api.moc_client import MOCClient

def fetch_rice_exports():
    print("Initializing MOC Client...")
    client = MOCClient()
    
    project_root = Path.cwd()
    output_dir = project_root / 'output/data'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    raw_path = output_dir / 'rice_exports_raw.csv'
    wide_path = output_dir / 'rice_exports_wide.csv'
    bilateral_path = output_dir / 'rice_exports_bilateral.csv'
    
    hs_code = "1006"
    
    # Establish target months: Jan 2024 to May 2026 (current month)
    current_year = 2026
    current_month = 5
    
    months_to_fetch = []
    for y in [2024, 2025, 2026]:
        for m in range(1, 12 + 1):
            if y == 2026 and m > current_month:
                continue
            months_to_fetch.append((y, m))
            
    print(f"Prepared sequence to fetch {len(months_to_fetch)} months of data for HS Code '{hs_code}'...")
    
    all_data = []
    
    for idx, (year, month) in enumerate(months_to_fetch):
        print(f"[{idx+1}/{len(months_to_fetch)}] Fetching bilateral exports for {year}-{month:02d}...")
        
        df = client.get_export_harmonize_countries(
            year=year,
            month=month,
            hs_code=hs_code,
            limit=999, # Retrieve all trading partners (MOC requires an explicit limit)
            force_refresh=False
        )
        
        if not df.empty:
            print(f"  -> Retrieved {len(df)} country records.")
            all_data.append(df)
        else:
            print(f"  -> No data or empty response for {year}-{month:02d}.")
            
        # Standard throttling to respect the MOC server
        time.sleep(0.5)
        
    if not all_data:
        print("[Error] No data retrieved from the MOC API. Execution halted.")
        return
        
    # Concatenate all months
    raw_df = pd.concat(all_data, ignore_index=True)
    
    # Cast date column
    raw_df['date'] = pd.to_datetime(raw_df['date'])
    
    # Save raw concatenated data
    raw_df.to_csv(raw_path, index=False, encoding='utf-8')
    print(f"\n[Success] Saved raw monthly data with {len(raw_df)} records to {raw_path}")
    
    # --- Pivot and Transform to Wide Format ---
    print("\nTransforming dataset to Wide Format standard...")
    
    # Fill in any missing or NaN values in critical columns
    raw_df['value_usd'] = pd.to_numeric(raw_df['value_usd'], errors='coerce').fillna(0.0)
    raw_df['quantity'] = pd.to_numeric(raw_df['quantity'], errors='coerce').fillna(0.0)
    raw_df['country_name_en'] = raw_df['country_name_en'].astype(str).str.strip().str.upper()
    
    # Group by Date and Country Name to ensure unique index key-value pairs before pivoting
    agg_df = raw_df.groupby(['date', 'country_name_en', 'country_code'])[['value_usd', 'quantity']].sum().reset_index()
    
    # 1. Wide Format standard: Date as index, English Country Names as columns
    wide_usd = agg_df.pivot(index='date', columns='country_name_en', values='value_usd').fillna(0.0)
    
    # Save standard wide format
    wide_usd.to_csv(wide_path, encoding='utf-8')
    print(f"[Success] Saved standard wide USD timeseries to {wide_path}")
    print(f"  -> Dimensions: {wide_usd.shape} (Months: {wide_usd.shape[0]}, Partners: {wide_usd.shape[1]})")
    
    # 2. Structural compatibility format (like durian_exports_bilateral.csv):
    # Lowercase country codes as column suffixes (e.g. rice_export_usd_cn)
    # Let's inspect country codes in raw_df
    print("\nPreviewing country code mappings:")
    print(agg_df[['country_code', 'country_name_en']].drop_duplicates().head(5).to_string(index=False))
    
    # Format country code column suffixes
    agg_df['country_code_lower'] = agg_df['country_code'].astype(str).str.strip().str.lower()
    agg_df['column_suffix'] = 'rice_export_usd_' + agg_df['country_code_lower']
    
    bilateral_wide = agg_df.pivot(index='date', columns='column_suffix', values='value_usd').fillna(0.0)
    
    # Save bilateral wide format
    bilateral_wide.to_csv(bilateral_path, encoding='utf-8')
    print(f"[Success] Saved structural wide USD timeseries to {bilateral_path}")
    print(f"  -> Dimensions: {bilateral_wide.shape} (Months: {bilateral_wide.shape[0]}, Partners: {bilateral_wide.shape[1]})")

if __name__ == "__main__":
    fetch_rice_exports()

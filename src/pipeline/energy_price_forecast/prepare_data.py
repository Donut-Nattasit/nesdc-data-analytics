import os
import sys
from datetime import datetime
import pandas as pd
from pathlib import Path
from src.api.eia_client import EIAClient

# Enforce UTF-8 encoding for standard console output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("==========================================================")
    print("[Dubai Oil Prep] Preparing Dubai Crude Oil Master Dataset...")
    print("==========================================================")
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    current_yyyy_mm = datetime.now().strftime("%Y-%m")
    excel_path = project_root / "input" / "pipeline" / "dubai_oil" / "dubai_price.xlsx"
    
    if not excel_path.exists():
        print(f"[Error] Excel file not found at: {excel_path}")
        raise RuntimeError("Pipeline step failed")
        
    # 1. Ingest Spot Dubai Prices
    print("\n[Step 1] Ingesting Spot Dubai Prices...")
    df_spot_raw = pd.read_excel(excel_path, sheet_name="spot")
    print(f"  Raw Spot Shape: {df_spot_raw.shape}")
    
    # Check date column
    df_spot_raw['date'] = pd.to_datetime(df_spot_raw['date'])
    
    # We want GIOS0097 Index as the default spot price.
    # Drop rows where GIOS0097 is null for resampling, but let's keep the date range clean.
    df_spot_valid = df_spot_raw.dropna(subset=['GIOS0097 Index']).copy()
    
    # Resample daily spot prices to Monthly frequency using Month-Start (MS) mean
    df_spot_monthly = df_spot_valid.resample('MS', on='date')[['GIOS0097 Index', 'PGCRDUBA Index']].mean().reset_index()
    df_spot_monthly = df_spot_monthly.rename(columns={
        'GIOS0097 Index': 'dubai_spot',
        'PGCRDUBA Index': 'dubai_spot_alt'
    })
    print(f"  Monthly Resampled Spot Shape: {df_spot_monthly.shape}")
    print(f"  Spot Date Range: {df_spot_monthly['date'].min().strftime('%Y-%m')} to {df_spot_monthly['date'].max().strftime('%Y-%m')}")
    
    # 2. Ingest Futures Dubai Prices
    print("\n[Step 2] Ingesting Futures Dubai Prices...")
    df_future_raw = pd.read_excel(excel_path, sheet_name="future")
    print(f"  Raw Futures Shape: {df_future_raw.shape}")
    df_future_raw['date'] = pd.to_datetime(df_future_raw['date'])
    
    # Resample daily futures to Monthly frequency using MS mean
    future_cols = [c for c in df_future_raw.columns if c.startswith('DBL')]
    df_future_monthly = df_future_raw.resample('MS', on='date')[future_cols].mean().reset_index()
    print(f"  Monthly Resampled Futures Shape: {df_future_monthly.shape}")
    print(f"  Futures Date Range: {df_future_monthly['date'].min().strftime('%Y-%m')} to {df_future_monthly['date'].max().strftime('%Y-%m')}")
    
    # 3. Retrieve EIA STEO monthly data
    print("\n[Step 3] Retrieving EIA STEO Monthly Data...")
    db_path = str(project_root / "database" / "energy_price_forecast" / "energy_price_forecast.db")
    eia_client = EIAClient(db_path=db_path)
    
    # Fetch price indicators (WTI and Brent spot prices)
    # force_refresh=True: STEO is published monthly; always fetch the latest release
    # to avoid serving the previous month's data from a still-"fresh" cache.
    print("  Fetching EIA Crude Prices (WTIPUUS, BREPUUS) [force_refresh=True]...")
    df_eia_prices = eia_client.get_data_steo(
        ['WTIPUUS', 'BREPUUS'], frequency='monthly', force_refresh=True
    )
    df_eia_prices = df_eia_prices.rename(columns={
        'WTIPUUS': 'wti_spot',
        'BREPUUS': 'brent_spot'
    })
    df_eia_prices['date'] = pd.to_datetime(df_eia_prices['date'])
    print(f"  EIA Prices Shape: {df_eia_prices.shape}")
    
    # Fetch world supply/demand/inventory indicators (PAPR_WORLD, PATC_WORLD, T3_STCHANGE_WORLD)
    # force_refresh=True: same rationale — always pull the latest STEO world balance.
    print("  Fetching EIA World Balance (PAPR_WORLD, PATC_WORLD, T3_STCHANGE_WORLD) [force_refresh=True]...")
    df_eia_balance = eia_client.get_data_steo(
        ['PAPR_WORLD', 'PATC_WORLD', 'T3_STCHANGE_WORLD'], frequency='monthly', force_refresh=True
    )
    df_eia_balance = df_eia_balance.rename(columns={
        'PAPR_WORLD': 'world_oil_supply',
        'PATC_WORLD': 'world_oil_demand',
        'T3_STCHANGE_WORLD': 'world_oil_inventory_change'
    })
    df_eia_balance['date'] = pd.to_datetime(df_eia_balance['date'])
    print(f"  EIA World Balance Shape: {df_eia_balance.shape}")
    
    # 4. Merge All Series into Master Wide-Format
    print("\n[Step 4] Merging Datasets...")
    # Base is spot price
    df_master = df_spot_monthly.copy()
    
    # Merge future prices
    df_master = pd.merge(df_master, df_future_monthly, on='date', how='outer')
    
    # Merge EIA prices
    df_master = pd.merge(df_master, df_eia_prices, on='date', how='outer')
    
    # Merge EIA world balance
    df_master = pd.merge(df_master, df_eia_balance, on='date', how='outer')
    
    # Sort by date
    df_master = df_master.sort_values(by='date').reset_index(drop=True)
    print(f"  Master Shape: {df_master.shape}")
    print(f"  Master Date Range: {df_master['date'].min().strftime('%Y-%m')} to {df_master['date'].max().strftime('%Y-%m')}")
    
    # Let's see some non-null stats for key variables
    print("\n[Step 5] Master Dataset Statistics (Non-null count by date range):")
    for col in ['dubai_spot', 'DBL1 Comdty', 'wti_spot', 'brent_spot', 'world_oil_inventory_change']:
        col_valid = df_master.dropna(subset=[col])
        if not col_valid.empty:
            print(f"  - {col:30} : {len(col_valid):4} valid, range: {col_valid['date'].min().strftime('%Y-%m')} to {col_valid['date'].max().strftime('%Y-%m')}")
            
    # Save the transformed dataset to wide format csv
    out_dir = project_root / "output" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "energy_price_forecast" / "dubai_oil_master.csv"
    # Ensure subdirectory exists
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_master.to_csv(out_path, index=False)
    print(f"\n✅ Master dataset successfully saved to: {out_path}")
    
    try:
    except Exception as e:
        
if __name__ == "__main__":
    main()

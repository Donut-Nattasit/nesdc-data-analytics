import os
import sys
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# Enforce UTF-8 encoding for standard console output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
current_yyyy_mm = datetime.now().strftime("%Y-%m")
sys.path.append(str(project_root))

from src.visualization.charts import configure_matplotlib_font, save_chart

def main():
    print("==========================================================")
    print("[US Production Viz] Generating U.S. Crude Production Chart...")
    print("==========================================================")
    
    raw_path = project_root / "temp" / "ceic_candidates_raw.csv"
    
    # 1. Load data
    if raw_path.exists():
        print(f"Loading data from raw cache: {raw_path}")
        df = pd.read_csv(raw_path)
    else:
        print("[Error] Raw data cache not found. Attempting to fetch fresh from CEIC...")
        from src.api.ceic_client import CeicSession
        session = CeicSession()
        if session.authenticate():
            df = session.get_data(["355221677", "520147117", "43155301"])
            if df.empty:
                print("[Error] Failed to fetch data from CEIC. Exiting.")
                raise RuntimeError("Pipeline step failed")
            # Save raw cache
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(raw_path, index=False)
        else:
            print("[Error] Failed to authenticate with CEIC. Exiting.")
            raise RuntimeError("Pipeline step failed")
            
    # 2. Filter for weekly series (ID 355221677) and transform
    df['date'] = pd.to_datetime(df['date'])
    df_weekly = df[df['series_id'] == 355221677].sort_values('date').copy()
    
    if df_weekly.empty:
        print("[Error] Weekly series 355221677 data not found in cache. Exiting.")
        raise RuntimeError("Pipeline step failed")
        
    print(f"Loaded {len(df_weekly)} weekly observations from {df_weekly['date'].min().strftime('%Y-%m-%d')} to {df_weekly['date'].max().strftime('%Y-%m-%d')}.")
    
    # Filter recent history (Jan 2024 - May 2026)
    df_weekly_recent = df_weekly[(df_weekly['date'] >= '2024-01-01') & (df_weekly['date'] <= '2026-05-31')].copy()
    df_weekly_recent.set_index('date', inplace=True)
    
    # Resample to monthly average (Mean, aligned at Month-End)
    df_monthly = df_weekly_recent[['value']].resample('ME').mean().reset_index()
    df_monthly['value_mbd'] = df_monthly['value'] / 1000.0  # Convert to million barrels per day (mb/d)
    
    # Save transformed data
    transformed_dir = project_root / "output" / "data" / "energy_price_forecast"
    transformed_dir.mkdir(parents=True, exist_ok=True)
    transformed_path = transformed_dir / "dubai_oil_us_crude_production.csv"
    df_monthly.to_csv(transformed_path, index=False)
    print(f"✅ Saved transformed monthly U.S. crude production to: {transformed_path}")

if __name__ == "__main__":
    main()

import os
import time
import pandas as pd
from pathlib import Path
from src.api.moc_client import MOCClient

def fetch_and_transform_top5():
    print("Initializing MOC Client for Top 5 Exports Refreshed Analysis...")
    client = MOCClient()
    
    project_root = Path.cwd()
    output_dir = project_root / 'output/data'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    raw_path = output_dir / 'thailand_top5_exports_refreshed_raw.csv'
    summary_path = output_dir / 'thailand_top5_exports_refreshed_summary.csv'
    
    hs_codes = {
        "85": "Electrical Machinery & Electronics",
        "84": "Mechanical Machinery & Boilers",
        "87": "Vehicles & Parts (Excl. Railway)",
        "71": "Precious Stones & Gems",
        "40": "Rubber and Rubber Articles"
    }
    
    # Target months: all of 2025, and available months of 2026 (up to May)
    months_to_fetch = []
    # 2025 (months 1-12)
    for m in range(1, 13):
        months_to_fetch.append((2025, m))
    # 2026 (months 1-5)
    for m in range(1, 6):
        months_to_fetch.append((2026, m))
        
    print(f"Prepared schedule to fetch {len(months_to_fetch)} months for {len(hs_codes)} HS2 sectors (Total: {len(months_to_fetch)*len(hs_codes)} calls)...")
    
    all_records = []
    
    call_idx = 0
    total_calls = len(months_to_fetch) * len(hs_codes)
    
    for hs_code, desc in hs_codes.items():
        print(f"\nProcessing sector: HS {hs_code} ({desc})")
        for year, month in months_to_fetch:
            call_idx += 1
            print(f"  [{call_idx}/{total_calls}] Querying HS {hs_code} for {year}-{month:02d}...")
            
            # Retrieve bilateral exports from API
            df = client.get_export_harmonize_countries(
                year=year,
                month=month,
                hs_code=hs_code,
                limit=999, # Explicit limit to capture all trading partners
                force_refresh=False
            )
            
            if not df.empty:
                # Add metadata columns
                df['hs_code_query'] = hs_code
                df['sector_name'] = desc
                df['value_usd'] = pd.to_numeric(df['value_usd'], errors='coerce').fillna(0.0)
                df['value_baht'] = pd.to_numeric(df['value_baht'], errors='coerce').fillna(0.0)
                df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0.0)
                all_records.append(df)
                print(f"    -> SUCCESS! Retrieved {len(df)} records.")
            else:
                print(f"    -> Empty or failed response for {year}-{month:02d}.")
                
            # Throttling delay
            time.sleep(0.4)
            
    if not all_records:
        print("[Error] No data retrieved. Execution halted.")
        return
        
    # Concatenate all raw bilateral records
    raw_df = pd.concat(all_records, ignore_index=True)
    raw_df.to_csv(raw_path, index=False, encoding='utf-8')
    print(f"\n[Success] Saved raw monthly country-level data to {raw_path}")
    
    # Cast year and month to integers to avoid type mismatch (e.g. objects/strings)
    raw_df['year'] = pd.to_numeric(raw_df['year'], errors='coerce').fillna(0).astype(int)
    raw_df['month'] = pd.to_numeric(raw_df['month'], errors='coerce').fillna(0).astype(int)
    
    # Monthly aggregates per sector (sum USD value across all countries)
    monthly_agg = raw_df.groupby(['year', 'month', 'hs_code_query', 'sector_name'])['value_usd'].sum().reset_index()
    
    # Identify available months in 2026
    months_2026 = sorted(monthly_agg[monthly_agg['year'] == 2026]['month'].unique())
    print(f"Available months in 2026: {months_2026}")
    
    summary_rows = []
    
    for hs_code, desc in hs_codes.items():
        sector_data = monthly_agg[monthly_agg['hs_code_query'] == hs_code]
        
        # 1. Full-Year 2025 sum
        data_2025 = sector_data[sector_data['year'] == 2025]
        usd_2025_full = data_2025['value_usd'].sum()
        
        # 2. Cumulative 2025 sum for the same period available in 2026
        data_2025_period = data_2025[data_2025['month'].isin(months_2026)]
        usd_2025_period = data_2025_period['value_usd'].sum()
        
        # 3. Cumulative 2026 sum
        data_2026_period = sector_data[(sector_data['year'] == 2026) & (sector_data['month'].isin(months_2026))]
        usd_2026_period = data_2026_period['value_usd'].sum()
        
        # YoY calculation
        yoy_growth = ((usd_2026_period / usd_2025_period) - 1) * 100 if usd_2025_period > 0 else 0.0
        
        summary_rows.append({
            'hs_code': f"HS {hs_code}",
            'sector_name': desc,
            'usd_2025_full': usd_2025_full,
            'usd_2025_period': usd_2025_period,
            'usd_2026_period': usd_2026_period,
            'yoy_growth_pct': yoy_growth,
            'months_included': f"Jan-{months_2026[-1]:02d}"
        })
        
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(summary_path, index=False, encoding='utf-8')
    print(f"[Success] Saved aggregated comparison summary to {summary_path}")
    print("\nUpdated Comparison Summary Table:")
    print(summary_df.to_string(index=False))

if __name__ == "__main__":
    fetch_and_transform_top5()

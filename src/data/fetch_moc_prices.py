import os
import sys
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime
from src.api.moc_client import MOCClient

# Reconfigure stdout to use UTF-8 to handle Thai characters safely in Windows terminals
sys.stdout.reconfigure(encoding='utf-8')


# Targeted Verification Group (Option 1)
TARGETED_PRODUCTS = ["P11009", "P11013", "P11028", "P11037", "P11038", "P11046"]

# Complete List from Notebook (Option 2)
FULL_PRODUCTS = [
    "P11009", "P11013", "P11028", "P11037", "P11038", "P11046",
    "P12004", "P12016", "P12017", "P12019", "P13001", "P13003",
    "P13005", "P13009", "P13011", "P13022", "P13033", "P13035",
    "P13038", "P13043", "P16006", "P16007", "P16011", "W16001",
    "W16002", "W16035", "W16041", "W16042", "W17001", "W17011",
    "W17013"
]

def fetch_moc_prices(all_products=False, force_refresh=False, from_date="2026-01-01", to_date=None):
    print("Initializing MOC Product Prices Fetcher...")
    project_root = Path.cwd()
    
    # Resolve and load metadata
    meta_path = project_root / 'database/metadata/moc_product_metadata.csv'
    output_dir = project_root / 'output/data/moc_prices'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading metadata from {meta_path.name}...")
    try:
        # Load CSV and clean columns
        meta_df = pd.read_csv(meta_path, encoding='utf-8')
        # Handle trailing commas/empty columns
        meta_df = meta_df.loc[:, ~meta_df.columns.str.contains('^Unnamed')]
        # Rename columns to ensure standard mapping
        meta_df.columns = [c.strip() for c in meta_df.columns]
        meta_mapping = {}
        for _, row in meta_df.iterrows():
            prod_code = str(row['รหัสสินค้า']).strip()
            meta_mapping[prod_code] = {
                'product_name_th': str(row['ชื่อสินค้า']).strip(),
                'category': str(row['หมวดหมู่สินค้า']).strip(),
                'sale_type': str(row['รูปแบบการขาย']).strip()
            }
        print(f"Loaded metadata for {len(meta_mapping)} product codes.")
    except Exception as e:
        print(f"[Warning] Failed to load or parse metadata: {e}. Proceeding without mappings.")
        meta_mapping = {}

    # Determine product IDs to fetch
    product_ids = FULL_PRODUCTS if all_products else TARGETED_PRODUCTS
    print(f"Target products to fetch ({len(product_ids)}): {product_ids}")

    # Set dates
    if not to_date:
        to_date = datetime.now().strftime("%Y-%m-%d")
    print(f"Query window: {from_date} to {to_date}")

    # Initialize Client
    client = MOCClient()
    success_count = 0
    fail_count = 0

    for i, prod_id in enumerate(product_ids, 1):
        print(f"\n[{i}/{len(product_ids)}] Processing Product ID: {prod_id}...")
        
        # Resolve metadata info
        prod_meta = meta_mapping.get(prod_id, {
            'product_name_th': 'Unknown',
            'category': 'Unknown',
            'sale_type': 'Unknown'
        })
        print(f"  Name: {prod_meta['product_name_th']} | Category: {prod_meta['category']} | Sale Type: {prod_meta['sale_type']}")
        
        try:
            # Call API via resilient client
            df = client.get_product_prices(
                product_id=prod_id,
                from_date=from_date,
                to_date=to_date,
                force_refresh=force_refresh
            )
            
            if df.empty:
                print(f"  [Warning] Received empty dataset for {prod_id}.")
                fail_count += 1
                continue
                
            # Add metadata columns
            df['product_id'] = prod_id
            df['product_name_th'] = prod_meta['product_name_th']
            df['category'] = prod_meta['category']
            df['sale_type'] = prod_meta['sale_type']
            
            # Reorder columns for clean presentation
            columns_order = ['date', 'price_min', 'price_max', 'product_id', 'product_name_th', 'category', 'sale_type']
            existing_cols = [c for c in columns_order if c in df.columns]
            df = df[existing_cols]
            
            # Export CSV
            out_file = output_dir / f"{prod_id}.csv"
            df.to_csv(out_file, index=False, encoding='utf-8')
            print(f"  [Success] Exported {len(df)} price observations to {out_file.relative_to(project_root)}")
            success_count += 1
            
        except Exception as e:
            print(f"  [Error] Failed to fetch/save data for {prod_id}: {e}")
            fail_count += 1
            
    print(f"\n==================================================")
    print(f"Acquisition Run Completed.")
    print(f"Total: {len(product_ids)} | Success: {success_count} | Failed/Skipped: {fail_count}")
    print(f"Raw outputs stored in: {output_dir.relative_to(project_root)}")
    print(f"==================================================")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="MOC Product Prices Fetcher")
    parser.add_argument('--all', action='store_true', help="Fetch all 31 products (Option 2) instead of targeted subset (Option 1)")
    parser.add_argument('--refresh', action='store_true', help="Force API refresh (bypass local cache)")
    parser.add_argument('--from-date', type=str, default="2026-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument('--to-date', type=str, default=None, help="End date (YYYY-MM-DD)")
    
    args = parser.parse_args()
    fetch_moc_prices(
        all_products=args.all,
        force_refresh=args.refresh,
        from_date=args.from_date,
        to_date=args.to_date
    )

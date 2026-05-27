import os
import sys
import sqlite3
import pandas as pd
from pathlib import Path

# Reconfigure stdout to use UTF-8 to handle Thai characters safely in Windows terminals
sys.stdout.reconfigure(encoding='utf-8')


def transform_moc_prices():
    print("Initializing MOC Product Prices Transformer...")
    project_root = Path.cwd()
    
    input_dir = project_root / 'output/data/moc_prices'
    output_dir = project_root / 'output/data/transformed'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    db_path = project_root / 'database/core/time_series.db'
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_csv = output_dir / 'moc_prices_wide.csv'

    # Find all product CSV files
    if not input_dir.exists():
        print(f"Error: Input directory {input_dir} does not exist. Fetch raw data first.")
        return
        
    csv_files = list(input_dir.glob('*.csv'))
    if not csv_files:
        print(f"Error: No CSV files found in {input_dir}.")
        return

    print(f"Found {len(csv_files)} product raw datasets. Compiling wide format...")

    # Load and compile series
    compiled_df = None

    for csv_file in csv_files:
        prod_id = csv_file.stem
        try:
            df = pd.read_csv(csv_file)
            if df.empty or 'date' not in df.columns:
                print(f"  [Warning] Skipping empty or invalid file {csv_file.name}")
                continue
                
            # Parse dates
            df['date'] = pd.to_datetime(df['date'])
            
            # Compute average price safely
            df['price_min'] = pd.to_numeric(df['price_min'], errors='coerce').fillna(0.0)
            df['price_max'] = pd.to_numeric(df['price_max'], errors='coerce').fillna(0.0)
            df['price_avg'] = (df['price_min'] + df['price_max']) / 2.0
            
            # Keep only necessary series
            temp_df = df[['date', 'price_min', 'price_max', 'price_avg']].copy()
            
            # Rename columns to incorporate product ID
            temp_df = temp_df.rename(columns={
                'price_min': f"{prod_id}_min",
                'price_max': f"{prod_id}_max",
                'price_avg': f"{prod_id}_avg"
            })
            
            # Set index to date for pivoting/merging
            temp_df = temp_df.set_index('date')
            
            if compiled_df is None:
                compiled_df = temp_df
            else:
                # Outer join to align different date series
                compiled_df = compiled_df.join(temp_df, how='outer')
                
            print(f"  [Compiled] Integrated series for {prod_id}.")
            
        except Exception as e:
            print(f"  [Error] Failed to process {csv_file.name}: {e}")

    if compiled_df is None or compiled_df.empty:
        print("Error: Compiled wide dataframe is empty.")
        return

    # Sort index (dates) chronologically
    compiled_df = compiled_df.sort_index()

    # Reset index to export date as a column
    wide_df = compiled_df.reset_index()

    # Save to transformed CSV
    wide_df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"\n[Success] Exported unified wide-format master dataset to: {output_csv.relative_to(project_root)}")

    # Write to local SQLite database (time_series.db)
    print(f"Registering wide series in SQLite database at {db_path.relative_to(project_root)}...")
    try:
        # Convert date back to string for SQLite storage
        sqlite_df = wide_df.copy()
        sqlite_df['date'] = sqlite_df['date'].dt.strftime('%Y-%m-%d')
        
        with sqlite3.connect(db_path) as conn:
            # Save or replace the master table
            sqlite_df.to_sql('moc_product_prices_wide', conn, if_exists='replace', index=False)
            conn.commit()
            
        print(f"[SQLite] Table 'moc_product_prices_wide' successfully updated with {len(sqlite_df)} rows and {len(sqlite_df.columns)} columns.")
    except Exception as e:
        print(f"[SQLite Error] Failed to write wide series to database: {e}")
        
    print("Transformation completed successfully.\n")

if __name__ == '__main__':
    transform_moc_prices()

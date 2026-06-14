import os
import sys
import json
import sqlite3
import pandas as pd
import time
from datetime import datetime
from pathlib import Path

# Override print to automatically flush stdout for background log visibility
_print = print
def print(*args, **kwargs):
    _print(*args, **kwargs)
    sys.stdout.flush()

# Add project root to sys.path to allow src imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from src.api.ceic_client import CeicSession
from src.utils.registry import add_dataset

def fetch_with_retry(sid, session, max_retries=5):
    from ceic_api_client.pyceic import Ceic
    delay = 2.0
    for attempt in range(max_retries):
        try:
            # 1. Try with historical extension
            try:
                res = Ceic.series([sid], with_historical_extension=True, count=10000)
                df = session._parse_response(res)
                if not df.empty:
                    return df
            except Exception as e:
                # 2. Try without historical extension if it is a non-continuous series
                if "NON_CONTINUOUS_SERIES" in str(e):
                    res = Ceic.series([sid], with_historical_extension=False, count=10000)
                    df = session._parse_response(res)
                    # If it successfully returns (even if empty), it's a valid API response, not a transient error.
                    return df
                else:
                    raise e
        except Exception as e:
            print(f"      [Attempt {attempt+1}/{max_retries}] Error fetching {sid}: {e}")
            
        print(f"      [Attempt {attempt+1}/{max_retries}] Empty response or rate limit for {sid}. Wait {delay:.1f}s...")
        time.sleep(delay)
        delay *= 2.0  # Exponential backoff
        
    return pd.DataFrame()

def main():
    print("==========================================================")
    print("[LR Ingestion] Preparing CPI and Weight Master Dataset (LR)...")
    print("==========================================================")
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    db_path = project_root / "database" / "energy_price_forecast_LR" / "energy_price_forecast_LR.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. Load mappings from config
    config_path = project_root / "src" / "pipeline" / "energy_price_forecast_LR" / "config" / "cpi_mapping.json"
    if not config_path.exists():
        print(f"[Error] Config file not found at: {config_path}")
        sys.exit(1)
        
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    cpi_indices = config["cpi_indices"]
    cpi_weights = config["cpi_weights"]
    prediction_targets_filter = config["prediction_targets_filter"]
    
    # Combine series IDs
    all_sids = list(set(list(cpi_indices.keys()) + list(cpi_weights.keys())))
    print(f"Total CEIC Series needed: {len(all_sids)}")
    
    # 2. Load cached raw data from seeded DB first
    df_cached = pd.DataFrame()
    cached_sids = set()
    
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cpi_raw_long'")
            if cursor.fetchone():
                print("Loading cached raw series from seeded database...")
                df_cached = pd.read_sql_query("SELECT * FROM cpi_raw_long", conn)
                if not df_cached.empty:
                    df_cached['series_id'] = df_cached['series_id'].astype(str)
                    cached_sids = set(df_cached['series_id'].tolist())
                    print(f"Loaded {len(cached_sids)} cached series from database.")
        except Exception as e:
            print(f"[Warning] Failed to read from DB cache: {e}")
        finally:
            conn.close()
            
    # Find which series IDs are missing
    missing_sids = [sid for sid in all_sids if sid not in cached_sids]
    
    # 3. Fetch missing series from CEIC if any
    df_new = pd.DataFrame()
    if missing_sids:
        print(f"\nMissing {len(missing_sids)} series from DB cache. Initializing CEIC Session...")
        ceic_session = CeicSession()
        if not ceic_session.authenticate():
            print("[FAIL] CEIC Authentication failed.")
            sys.exit(1)
            
        print(f"Fetching {len(missing_sids)} missing series individually with retries...")
        retry_dfs = []
        for i, sid in enumerate(missing_sids):
            print(f"  Fetching series {i+1}/{len(missing_sids)}: {sid}...")
            df_single = fetch_with_retry(sid, ceic_session)
            if not df_single.empty:
                retry_dfs.append(df_single)
            else:
                print(f"  [FAIL] Could not fetch series {sid}")
                
        mapping_dict = {**cpi_indices, **cpi_weights}
        if retry_dfs:
            df_new = pd.concat(retry_dfs, ignore_index=True)
            df_new['series_id'] = df_new['series_id'].astype(str)
            fetched_sids = set(df_new['series_id'].tolist())
        else:
            df_new = pd.DataFrame()
            fetched_sids = set()
            
        still_missing = [sid for sid in missing_sids if sid not in fetched_sids]
        critically_missing = []
        for sid in still_missing:
            name = mapping_dict.get(sid)
            if name in prediction_targets_filter:
                critically_missing.append((sid, name))
                
        if critically_missing:
            print(f"[FAIL] Still missing critical series required for forecasting: {critically_missing}")
            sys.exit(1)
        else:
            if still_missing:
                print(f"[Warning] Skipped missing non-critical series: {[(sid, mapping_dict.get(sid)) for sid in still_missing]}")

    # Combine cached and new data
    if not df_cached.empty or not df_new.empty:
        df_raw = pd.concat([df_cached, df_new], ignore_index=True)
        # Deduplicate
        df_raw = df_raw.drop_duplicates(subset=['date', 'series_id']).reset_index(drop=True)
    else:
        print("[FAIL] No data available (cache and API fetch both empty).")
        sys.exit(1)
        
    print(f"Total raw dataset contains {len(df_raw)} observations across {df_raw['series_id'].nunique()} series.")
    
    # Save combined raw data to database
    print("\n[Step 2] Caching raw data to SQLite database...")
    conn = sqlite3.connect(str(db_path))
    try:
        df_raw_write = df_raw.copy()
        df_raw_write['date'] = df_raw_write['date'].astype(str)
        df_raw_write.to_sql("cpi_raw_long", conn, if_exists="replace", index=False)
        conn.commit()
    except Exception as e:
        print(f"[Warning] Failed to write raw table to database: {e}")
    
    # Transform to wide format
    print("\n[Step 3] Pivoting to Wide Format and renaming columns...")
    df_raw['series_id'] = df_raw['series_id'].astype(str)
    df_pivot = df_raw.pivot(index='date', columns='series_id', values='value')
    df_pivot.index = pd.to_datetime(df_pivot.index)
    df_pivot = df_pivot.sort_index()
    
    # Save a copy with raw series IDs to database
    try:
        df_pivot_write = df_pivot.copy()
        df_pivot_write.index = df_pivot_write.index.strftime('%Y-%m-%d')
        df_pivot_write.to_sql("cpi_raw_wide_ids", conn, if_exists="replace", index=True)
        conn.commit()
    except Exception as e:
        print(f"[Warning] Failed to write raw wide table to database: {e}")
        
    # Rename using combined mapping dict
    mapping_dict = {**cpi_indices, **cpi_weights}
    df_renamed = df_pivot.rename(columns=mapping_dict)
    
    # Save renamed wide table to database
    try:
        df_renamed_write = df_renamed.copy()
        df_renamed_write.index = df_renamed_write.index.strftime('%Y-%m-%d')
        df_renamed_write.to_sql("cpi_raw_wide_names", conn, if_exists="replace", index=True)
        conn.commit()
    except Exception as e:
        print(f"[Warning] Failed to write raw wide names table: {e}")
        
    # 4. Ingest Exogenous Dubai Oil Price Prediction (Excel)
    print("\n[Step 4] Ingesting Exogenous Dubai Crude Oil Forecasts from Excel...")
    dubai_path = project_root / "input" / "oil_price_forecast_LR" / "dubai_oil_price_forecast_LR.xlsx"
    if not dubai_path.exists():
        print(f"[FAIL] Exogenous Dubai Oil forecast file not found at: {dubai_path}")
        sys.exit(1)
        
    df_dubai = pd.read_excel(dubai_path, sheet_name="Sheet1")
    df_dubai = df_dubai.rename(columns={"Unnamed: 0": "date"})
    df_dubai["date"] = pd.to_datetime(df_dubai["date"])
    df_dubai = df_dubai.set_index("date").sort_index()
    print(f"Loaded Dubai Crude Oil forecast. Shape: {df_dubai.shape}")
    
    # 5. Perform Reverse Engineering
    print("\n[Step 5] Performing Reverse Engineering of weights and indices...")
    df_clean = df_renamed.copy()
    
    # Derive weights
    df_clean["CPI: Weights: Housing & Furnishing (HF): Utilities"] = (
        df_clean["Non Core CPI: Weights: Raw Food and Energy: Energy"] - 
        df_clean["CPI: Weights: TC: Vehicles & Vehicle Operation: Motor Fuel"]
    )
    df_clean["CPI: Weights: Housing & Furnishing (HF): ex Utilities"] = (
        df_clean["CPI: Weights: Housing & Furnishing (HF)"] - 
        df_clean["CPI: Weights: Housing & Furnishing (HF): Utilities"]
    )
    df_clean["CPI: Weights: Transport & Communication (TC): ex Motor Fuel"] = (
        df_clean["CPI: Weights: Transport & Communication (TC)"] - 
        df_clean["CPI: Weights: TC: Vehicles & Vehicle Operation: Motor Fuel"]
    )
    
    # Derive Indices
    df_clean["CPI: Housing & Furnishing (HF): Utilities"] = df_clean["CPI: HF: Electricity, Fuel, Water Supply"]
    
    idx_hf = df_clean["CPI: Housing & Furnishing (HF)"]
    w_hf = df_clean["CPI: Weights: Housing & Furnishing (HF)"]
    idx_ut = df_clean["CPI: Housing & Furnishing (HF): Utilities"]
    w_ut = df_clean["CPI: Weights: Housing & Furnishing (HF): Utilities"]
    w_ex_ut = df_clean["CPI: Weights: Housing & Furnishing (HF): ex Utilities"]
    df_clean["CPI: Housing & Furnishing (HF): ex Utilities"] = (idx_hf * w_hf - idx_ut * w_ut) / w_ex_ut
    
    df_clean["CPI: Transport & Communication (TC): Motor Fuel"] = df_clean["CPI: TC: Vehicles & Vehicle Operation: Motor Fuel"]
    
    idx_tc = df_clean["CPI: Transport & Communication (TC)"]
    w_tc = df_clean["CPI: Weights: Transport & Communication (TC)"]
    idx_mf = df_clean["CPI: Transport & Communication (TC): Motor Fuel"]
    w_mf = df_clean["CPI: Weights: TC: Vehicles & Vehicle Operation: Motor Fuel"]
    w_ex_mf = df_clean["CPI: Weights: Transport & Communication (TC): ex Motor Fuel"]
    df_clean["CPI: Transport & Communication (TC): ex Motor Fuel"] = (idx_tc * w_tc - idx_mf * w_mf) / w_ex_mf
    
    # 6. Filter to targets
    print("\n[Step 6] Filtering to targets and merging exogenous Dubai oil forecasts...")
    targets_map = {
        "CPI: FB: CH: Rice, Flour & Cereal (RF)": "index_Rice_Flour_Cereal",
        "CPI: FB: CH: Meats Poultry & Fish (MF)": "index_Meats_Poultry_Fish",
        "CPI: FB: CH: Eggs and Dairy Products": "index_Eggs_Dairy_Products",
        "CPI: FB: CH: Vegetables and Fruits": "index_Vegetables_Fruits",
        "CPI: FB: CH: Seasoning and Condiments (SC)": "index_Seasoning_Condiments",
        "CPI: FB: CH: Non Alcoholic Beverages": "index_Non_Alcoholic_Beverages",
        "CPI: FB: CH: Sugar Product: Sugar & Sweets": "index_Sugar_Product",
        "CPI: FB: Prepared Food": "index_Prepared_Food",
        "CPI: Apparel & Footwears (CF)": "index_Apparel_Footwears",
        "CPI: Housing & Furnishing (HF): ex Utilities": "index_Housing_Furnishing_ex_Utility",
        "CPI: Housing & Furnishing (HF): Utilities": "index_Housing_Furnishing_Utility",
        "CPI: Medical & Personal Care (HP)": "index_Medical_Personal_Care",
        "CPI: Transport & Communication (TC): ex Motor Fuel": "index_Transport_Communication_ex_Motor_Fuel",
        "CPI: Transport & Communication (TC): Motor Fuel": "index_Transport_Communication_Motor_Fuel",
        "CPI: Recreation, Reading, Education and Religion (RR)": "index_Recreation_Reading_Education_Religion",
        "CPI: Tobacco & Alcoholic Beverages (TA)": "index_Tobacco_Alcoholic_Beverages",
        
        "CPI: Weights: FB: CH: Rice, Flour & Cereal (RF)": "weight_Rice_Flour_Cereal",
        "CPI: Weights: FB: CH: Meats Poultry & Fish (MF)": "weight_Meats_Poultry_Fish",
        "CPI: Weights: FB: CH: Eggs and Dairy Products": "weight_Eggs_Dairy_Products",
        "CPI: Weights: FB: CH: Vegetables and Fruits": "weight_Vegetables_Fruits",
        "CPI: Weights: FB: CH: Seasoning and Condiments (SC)": "weight_Seasoning_Condiments",
        "CPI: Weights: FB: CH: Non Alcoholic Beverages": "weight_Non_Alcoholic_Beverages",
        "CPI: Weights: FB: CH: SC: Sugar & Sweet Products": "weight_Sugar_Product",
        "CPI: Weights: FB: Prepared Food": "weight_Prepared_Food",
        "CPI: Weights: Apparel & Footwears (CF)": "weight_Apparel_Footwears",
        "CPI: Weights: Housing & Furnishing (HF): ex Utilities": "weight_Housing_Furnishing_ex_Utility",
        "CPI: Weights: Housing & Furnishing (HF): Utilities": "weight_Housing_Furnishing_Utility",
        "CPI: Weights: Medical & Personal Care (HP)": "weight_Medical_Personal_Care",
        "CPI: Weights: Transport & Communication (TC): ex Motor Fuel": "weight_Transport_Communication_ex_Motor_Fuel",
        "CPI: Weights: TC: Vehicles & Vehicle Operation: Motor Fuel": "weight_Transport_Communication_Motor_Fuel",
        "CPI: Weights: Recreation, Reading, Education and Religion (RR)": "weight_Recreation_Reading_Education_Religion",
        "CPI: Weights: Tobacco & Alcoholic Beverages (TA)": "weight_Tobacco_Alcoholic_Beverages",
    }
    
    missing_cols = [col for col in targets_map.keys() if col not in df_clean.columns]
    if missing_cols:
        print(f"[FAIL] Missing expected columns for target mapping: {missing_cols}")
        sys.exit(1)
        
    df_targets = df_clean[list(targets_map.keys())].rename(columns=targets_map)
    
    # Merge with exogenous Dubai Crude Oil forecast
    df_merged = pd.merge(df_targets, df_dubai[['dubai_spot_forecast']], left_index=True, right_index=True, how='left')
    df_merged = df_merged.rename(columns={'dubai_spot_forecast': 'exog_dubai_crude'})
    
    # Drop rows where target indices are entirely null
    index_cols = [c for c in df_merged.columns if c.startswith('index_')]
    df_master = df_merged.dropna(subset=index_cols, how='all').copy()
    
    # 6. Save master clean data
    out_path = project_root / "output" / "data" / "energy_price_forecast_LR" / "cpi_historical_master.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    df_master.to_csv(out_path, index=True, index_label='date')
    print(f"\n[OK] Historical Master dataset saved to: {out_path}")
    print(f"Shape: {df_master.shape}")
    print(f"Date range: {df_master.index.min().strftime('%Y-%m-%d')} to {df_master.index.max().strftime('%Y-%m-%d')}")
    
    # Write transformed table to SQLite DB
    try:
        df_master_write = df_master.copy()
        df_master_write.index = df_master_write.index.strftime('%Y-%m-%d')
        df_master_write.to_sql("cpi_historical_master", conn, if_exists="replace", index=True, index_label='date')
        conn.commit()
        print("[OK] Saved table 'cpi_historical_master' to SQLite.")
    except Exception as e:
        print(f"[Warning] Failed to write clean master table: {e}")
    finally:
        conn.close()
        
    # Register dataset in PROJECT_STATE.json
    try:
        add_dataset(
            series_id="CPI Forecasting Historical Master Wide (LR)",
            source="CEIC API & Dubai Crude Long-Range Excel Forecast",
            raw_path="database/energy_price_forecast_LR/energy_price_forecast_LR.db (table: cpi_raw_long)",
            transformed_path="output/data/energy_price_forecast_LR/cpi_historical_master.csv",
            forecast_path="",
            status="Ready",
            last_update=pd.Timestamp.now().strftime('%Y-%m-%d')
        )
        print("[OK] Registered dataset in PROJECT_STATE.json.")
    except Exception as e:
        print(f"[Warning] Registry update failed: {e}")

if __name__ == "__main__":
    print("Execution timestamp:", datetime.now())
    main()

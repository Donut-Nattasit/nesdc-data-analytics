import os
import sqlite3
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def pad_code(val, length):
    if pd.isna(val):
        return val
    try:
        # Convert to float then int, or directly string to remove decimal
        if isinstance(val, float) and val.is_integer():
            val = int(val)
        val_str = str(val).strip()
        if val_str.endswith('.0'):
            val_str = val_str[:-2]
        
        # If it's a number, pad it
        if val_str.isdigit():
            return val_str.zfill(length)
        return val_str
    except Exception:
        return str(val).strip()

def main():
    project_root = Path(__file__).resolve().parents[2]
    db_path = project_root / "database" / "DBD.db"
    excel_path = project_root / "input" / "งบการเงิน" / "TSIC_descriptions.xlsx"
    
    if not excel_path.exists():
        print(f"Error: Excel file {excel_path} not found.")
        sys.exit(1)
        
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(str(db_path))
    
    # Mapping sheet names to tables, specifying columns to pad and their lengths
    sheets_config = {
        "mapping": {
            "table": "tsic_mapping",
            "pads": {
                "หมวดย่อย": 2,
                "หมู่ใหญ่": 3,
                "หมู่ย่อย": 4,
                "กิจกรรม": 5
            }
        },
        "หมวดใหญ่": {
            "table": "tsic_category",
            "pads": {} # No padding needed
        },
        "หมวดย่อย": {
            "table": "tsic_division",
            "pads": {
                "หมวดย่อย": 2
            }
        },
        "หมู่ใหญ่": {
            "table": "tsic_group",
            "pads": {
                "หมู่ใหญ่": 3
            }
        },
        "หมู่ย่อย": {
            "table": "tsic_class",
            "pads": {
                "หมู่ย่อย": 4
            }
        },
        "กิจกรรม": {
            "table": "tsic_activity",
            "pads": {
                "กิจกรรม": 5
            }
        }
    }
    
    xl = pd.ExcelFile(excel_path)
    
    for sheet_name, config in sheets_config.items():
        if sheet_name not in xl.sheet_names:
            print(f"Warning: Sheet {sheet_name} not found in Excel. Skipping.")
            continue
            
        print(f"Reading sheet: {sheet_name}...")
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        # Clean columns and strings
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
                
        # Pad columns according to config
        for col_to_pad, length in config["pads"].items():
            if col_to_pad in df.columns:
                print(f"  Padding column '{col_to_pad}' to length {length}")
                df[col_to_pad] = df[col_to_pad].apply(lambda x: pad_code(x, length))
        
        table_name = config["table"]
        print(f"  Writing {len(df)} rows to table '{table_name}'...")
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
    conn.close()
    print("Successfully processed all TSIC sheets.")
    

if __name__ == "__main__":
    main()

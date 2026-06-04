import os
import glob
import sqlite3
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.utils.registry import add_dataset

def clean_value(val):
    if isinstance(val, str):
        val = val.strip()
        if val.startswith("'"):
            val = val[1:]
        if val.endswith("'"):
            val = val[:-1]
        return val.strip()
    return val

def clean_dataframe(df):
    # Apply clean_value to object/string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(clean_value)
    return df

def main():
    project_root = Path(__file__).resolve().parents[2]
    db_dir = project_root / "database" / "core"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "DBD.db"
    
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(str(db_path))
    
    # Define source folders and corresponding entity_type
    sources = [
        {
            "dir": project_root / "input" / "งบการเงิน" / "บริษัทจำกัด" / "data",
            "type": "บริษัทจำกัด"
        },
        {
            "dir": project_root / "input" / "งบการเงิน" / "ห้างหุ้นส่วนจำกัด" / "data",
            "type": "ห้างหุ้นส่วนจำกัด"
        }
    ]
    
    table_name = "financial_statements"
    chunk_size = 50000
    total_rows = 0
    
    # Specify dtypes to prevent mixed-type warnings and preserve formatting
    dtype_dict = {
        'เลขทะเบียน': str,
        'รหัสไปรษณีย์': str,
        'รหัสวัตถุประสงค์': str,
        'รหัสกลุ่มวัตถุประสงค์': str,
        'ประเภทข้อมูล': str
    }
    
    is_first_write = True
    
    for source in sources:
        folder = source["dir"]
        entity_type = source["type"]
        
        print(f"Scanning folder: {folder}")
        if not folder.exists():
            print(f"Warning: Folder {folder} does not exist. Skipping.")
            continue
            
        csv_files = sorted(glob.glob(os.path.join(folder, "*.csv")))
        print(f"Found {len(csv_files)} CSV files for {entity_type}")
        
        for csv_file in csv_files:
            file_name = os.path.basename(csv_file)
            print(f"Processing {file_name}...")
            
            # Read in chunks using cp874 to avoid decoding errors
            chunks = pd.read_csv(
                csv_file, 
                encoding='cp874', 
                chunksize=chunk_size, 
                dtype=dtype_dict,
                low_memory=False
            )
            
            for chunk_idx, chunk in enumerate(chunks):
                # Clean the chunk
                chunk = clean_dataframe(chunk)
                
                # Add the entity_type column
                chunk["entity_type"] = entity_type
                
                # Write to database
                if is_first_write:
                    chunk.to_sql(table_name, conn, if_exists='replace', index=False)
                    is_first_write = False
                else:
                    chunk.to_sql(table_name, conn, if_exists='append', index=False)
                
                total_rows += len(chunk)
                
            print(f"Finished {file_name}. Cumulative rows written: {total_rows}")
            
    conn.close()
    print(f"Successfully wrote {total_rows} total rows to table '{table_name}' in DBD.db.")
    
    # Register the dataset in the manifest
    add_dataset(
        series_id="DBD Financial Statements",
        source="Department of Business Development (DBD)",
        raw_path="input/งบการเงิน",
        transformed_path="database/core/DBD.db",
        forecast_path="",
        status="Ready"
    )

if __name__ == "__main__":
    main()

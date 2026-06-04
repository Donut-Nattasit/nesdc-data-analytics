import os
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def main():
    project_root = Path(__file__).resolve().parents[2]
    db_path = project_root / "database" / "core" / "DBD.db"
    
    if not db_path.exists():
        print(f"Error: Database {db_path} not found.")
        sys.exit(1)
        
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(str(db_path))
    
    print("Loading financial_statements table...")
    df = pd.read_sql_query("SELECT * FROM financial_statements", conn)
    print(f"Loaded {len(df)} rows.")
    
    print("Loading TSIC mapping...")
    tsic_df = pd.read_sql_query("SELECT [กิจกรรม], [หมวดใหญ่] FROM tsic_mapping", conn)
    print(f"Loaded {len(tsic_df)} TSIC mapping rows.")
    
    # Ensure code columns are clean strings for merging
    df['รหัสวัตถุประสงค์_clean'] = df['รหัสวัตถุประสงค์'].astype(str).str.strip()
    tsic_df['กิจกรรม_clean'] = tsic_df['กิจกรรม'].astype(str).str.strip()
    
    # Merge with TSIC mapping to get หมวดใหญ่ (Section)
    print("Mapping TSIC categories...")
    df = df.merge(tsic_df, left_on='รหัสวัตถุประสงค์_clean', right_on='กิจกรรม_clean', how='left')
    
    # Clean and cast financial columns to float
    financial_cols = [
        'ทุนจดทะเบียน(งบ)', 'ทุนชำระแล้ว(งบ)', 'ที่ดิน อาคาร และอุปกรณ์', 
        'สินทรัพย์หมุนเวียน', 'สินทรัพย์', 'ลูกหนี้การค้า', 'หนี้สินหมุนเวียน', 
        'หนี้สิน', 'สินค้าคงเหลือ', 'ส่วนของผู้เป็นหุ้นส่วน/ผู้ถือหุ้น', 
        'รายได้จากการขาย', 'รายได้จากการบริการ', 'รายได้จากการขายหรือบริการ', 
        'รายได้อื่น', 'ต้นทุนการให้บริการ', 'ต้นทุนขายหรือต้นทุนการให้บริการ', 
        'รวมรายได้', 'ต้นทุนขาย (รวม)', 'ดอกเบี้ยจ่าย', 'ภาษีเงินได้', 
        'รวมรายจ่าย', 'กำไร (ขาดทุนสุทธิ)', 'กำไรขั้นต้น'
    ]
    
    print("Converting financial fields from text with commas to clean numeric (REAL) values...")
    for col in financial_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '', regex=False).str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            
    # Exclude firms with negative revenue (outliers)
    num_neg = (df['รวมรายได้'] < 0.0).sum()
    print(f"Excluding {num_neg} firms with negative 'รวมรายได้' as outliers.")
    df = df[df['รวมรายได้'] >= 0.0].copy()
    
    # Classify Firm_Size using the cleaned revenue
    print("Classifying Firm_Size...")
    
    # Pre-calculate condition masks
    is_agri_ind = df['หมวดใหญ่'].isin(['A', 'B', 'C', 'D', 'E'])
    rev = df['รวมรายได้']
    
    # Conditions list
    conditions = [
        # Agricultural + Industrial (A-E)
        is_agri_ind & (rev <= 100_000_000.0),
        is_agri_ind & (rev <= 500_000_000.0),
        is_agri_ind & (rev > 500_000_000.0),
        
        # Services & Others (F-U, missing category defaults to Services)
        (~is_agri_ind) & (rev <= 50_000_000.0),
        (~is_agri_ind) & (rev <= 300_000_000.0),
        (~is_agri_ind) & (rev > 300_000_000.0)
    ]
    
    # Choice list corresponding to conditions
    choices = ['S', 'M', 'L', 'S', 'M', 'L']
    
    # Assign firm_size
    df['firm_size'] = np.select(conditions, choices, default='S')
    
    # Clean up temporary columns
    columns_to_drop = ['รหัสวัตถุประสงค์_clean', 'กิจกรรม', 'หมวดใหญ่', 'กิจกรรม_clean']
    df = df.drop(columns=columns_to_drop, errors='ignore')
    
    # Define explicit SQLite types for string columns to prevent SQLite from mapping them automatically
    dtype_dict = {
        'เลขทะเบียน': 'TEXT',
        'รหัสไปรษณีย์': 'TEXT',
        'รหัสวัตถุประสงค์': 'TEXT',
        'รหัสกลุ่มวัตถุประสงค์': 'TEXT',
        'ประเภทข้อมูล': 'TEXT',
        'entity_type': 'TEXT',
        'firm_size': 'TEXT'
    }
    
    print("Writing classified and cleaned table back to DBD.db...")
    # Overwrite the table
    df.to_sql("financial_statements", conn, if_exists='replace', index=False, dtype=dtype_dict)
    
    # Print sample counts
    print("\nFirm Size Classifications Summary:")
    counts = df['firm_size'].value_counts()
    for size, count in counts.items():
        print(f"  {size}: {count:,} firms")
        
    conn.close()
    print("\nSuccessfully finished firm size classification!")

if __name__ == "__main__":
    main()

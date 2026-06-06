import sqlite3
import pandas as pd
from pathlib import Path

def extract_thailand_exports():
    project_root = Path.cwd()
    db_path = project_root / 'database/GTA.db'
    output_dir = project_root / 'output/data'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'thailand_top5_exports_raw.csv'
    
    conn = sqlite3.connect(db_path)
    
    # Step 1: Find the top 5 HS2 codes in 2025 by total export value
    top_5_query = """
    SELECT HS2_Code, SUM(USD) as Total_USD
    FROM GTA
    WHERE Reporter_ISO = 'TH'
      AND Trade_Direction = 'Export'
      AND Year = 2025
    GROUP BY HS2_Code
    ORDER BY Total_USD DESC
    LIMIT 5
    """
    top_5_df = pd.read_sql_query(top_5_query, conn)
    top_5_hs2 = top_5_df['HS2_Code'].tolist()
    print(f"Top 5 HS2 categories identified: {top_5_hs2}")
    
    # Step 2: Fetch all monthly export data for these top 5 HS2 codes in 2025 and 2026
    hs_list_str = ','.join(map(str, top_5_hs2))
    detailed_query = f"""
    SELECT 
        t.Year,
        t.Month,
        t.HS2_Code,
        h.HS2_Desc_EN,
        t.USD
    FROM GTA t
    LEFT JOIN meta_hs2 h ON t.HS2_Code = h.HS2_Code
    WHERE t.Reporter_ISO = 'TH'
      AND t.Trade_Direction = 'Export'
      AND t.HS2_Code IN ({hs_list_str})
      AND t.Year IN (2025, 2026)
    ORDER BY t.Year, t.Month, t.HS2_Code
    """
    df = pd.read_sql_query(detailed_query, conn)
    
    # Step 3: Save to raw CSV
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Successfully extracted {len(df)} records to {output_path}")
    
    conn.close()

if __name__ == '__main__':
    extract_thailand_exports()

import sqlite3
import pandas as pd
import numpy as np
import os

def main():
    db_path = 'database/DBD.db'
    output_dir = 'output/data'
    output_file = os.path.join(output_dir, 'hhi_tsic4.csv')
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    
    # 1. Load active firms for fiscal year 2566
    print("Loading financial statements...")
    query_firms = """
    SELECT 
        [เลขทะเบียน] AS firm_id,
        [ชื่อนิติบุคคล] AS firm_name,
        [รหัสวัตถุประสงค์] AS objective_code,
        [รายได้จากการขายหรือบริการ] AS revenue
    FROM financial_statements
    WHERE [สถานะนิติบุคคล] = '1'
      AND [ปีงบการเงิน] = 2566
    """
    df_firms = pd.read_sql_query(query_firms, conn)
    # Drop records with missing or empty objective code
    df_firms = df_firms.dropna(subset=['objective_code'])
    df_firms = df_firms[df_firms['objective_code'].astype(str).str.strip() != '']
    print(f"Loaded {len(df_firms):,} records after filtering empty objective codes.")
    
    # 2. Extract 4-digit TSIC code
    df_firms['tsic4'] = df_firms['objective_code'].astype(str).str.slice(0, 4)
    
    # Clean revenue: convert to numeric, replace NaNs with 0
    df_firms['revenue'] = pd.to_numeric(df_firms['revenue'], errors='coerce').fillna(0.0)
    
    # 3. Calculate total active firms per 4-digit TSIC (including 0 revenue)
    print("Calculating active firm counts...")
    df_total_firms = df_firms.groupby('tsic4')['firm_id'].count().reset_index(name='active_firms')
    
    # 4. Filter for firms with positive revenue
    df_pos = df_firms[df_firms['revenue'] > 0].copy()
    print(f"Firms with positive revenue: {len(df_pos):,} (out of {len(df_firms):,})")
    
    # Sort descending by TSIC and Revenue to compute CR ratios
    df_pos = df_pos.sort_values(['tsic4', 'revenue'], ascending=[True, False])
    
    # Calculate total revenue per industry
    print("Computing total revenues per industry...")
    df_pos['total_revenue'] = df_pos.groupby('tsic4')['revenue'].transform('sum')
    df_pos['share'] = df_pos['revenue'] / df_pos['total_revenue']
    df_pos['share_pct'] = df_pos['share'] * 100
    df_pos['share_pct_sq'] = df_pos['share_pct'] ** 2
    
    # Sum of squared shares to get HHI
    print("Computing HHI...")
    df_hhi = df_pos.groupby('tsic4')['share_pct_sq'].sum().reset_index(name='hhi')
    
    # Count of firms with positive revenue
    df_pos_counts = df_pos.groupby('tsic4')['firm_id'].count().reset_index(name='firms_with_revenue')
    
    # Sum of revenues
    df_rev_sum = df_pos.groupby('tsic4')['revenue'].sum().reset_index(name='total_revenue')
    
    # Compute Concentration Ratios (CR1, CR4, CR8)
    print("Computing Concentration Ratios (CR1, CR4, CR8)...")
    df_pos['rank'] = df_pos.groupby('tsic4').cumcount() + 1
    
    df_cr1 = df_pos[df_pos['rank'] <= 1].groupby('tsic4')['share'].sum().reset_index(name='cr1')
    df_cr4 = df_pos[df_pos['rank'] <= 4].groupby('tsic4')['share'].sum().reset_index(name='cr4')
    df_cr8 = df_pos[df_pos['rank'] <= 8].groupby('tsic4')['share'].sum().reset_index(name='cr8')
    
    # 5. Merge all calculations
    print("Merging metrics...")
    df_metrics = df_total_firms.merge(df_pos_counts, on='tsic4', how='left')
    df_metrics = df_metrics.merge(df_rev_sum, on='tsic4', how='left')
    df_metrics = df_metrics.merge(df_hhi, on='tsic4', how='left')
    df_metrics = df_metrics.merge(df_cr1, on='tsic4', how='left')
    df_metrics = df_metrics.merge(df_cr4, on='tsic4', how='left')
    df_metrics = df_metrics.merge(df_cr8, on='tsic4', how='left')
    
    # Fill NaNs for industries with 0 revenue firms
    df_metrics['firms_with_revenue'] = df_metrics['firms_with_revenue'].fillna(0).astype(int)
    df_metrics['total_revenue'] = df_metrics['total_revenue'].fillna(0.0)
    df_metrics['hhi'] = df_metrics['hhi'].fillna(0.0)
    df_metrics['cr1'] = df_metrics['cr1'].fillna(0.0)
    df_metrics['cr4'] = df_metrics['cr4'].fillna(0.0)
    df_metrics['cr8'] = df_metrics['cr8'].fillna(0.0)
    
    # 6. Load TSIC class descriptions
    print("Loading TSIC descriptions...")
    query_desc = """
    SELECT 
        [หมู่ย่อย] AS tsic4,
        [คำอธิบาย] AS desc_th,
        [Description] AS desc_en
    FROM tsic_class
    """
    df_desc = pd.read_sql_query(query_desc, conn)
    
    # Merge descriptions
    df_final = df_metrics.merge(df_desc, on='tsic4', how='left')
    
    # Clean descriptions (fill nulls)
    df_final['desc_th'] = df_final['desc_th'].fillna('ไม่ทราบคำอธิบาย')
    df_final['desc_en'] = df_final['desc_en'].fillna('Unknown Description')
    
    # Reorder columns
    cols = [
        'tsic4', 'desc_th', 'desc_en', 'active_firms', 'firms_with_revenue', 
        'total_revenue', 'hhi', 'cr1', 'cr4', 'cr8'
    ]
    df_final = df_final[cols]
    
    # Sort by total revenue descending
    df_final = df_final.sort_values('total_revenue', ascending=False)
    
    # Save to CSV
    df_final.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"Successfully computed HHI and saved to: {output_file}")
    
    # Print high-level summary
    print("\n=== Market Concentration Summary (TSIC4) ===")
    print(f"Total Industries Analyzed: {len(df_final)}")
    
    # Top 5 most concentrated industries (HHI >= 2500 is considered highly concentrated)
    highly_concentrated = df_final[df_final['hhi'] >= 2500]
    print(f"Highly Concentrated Industries (HHI >= 2,500): {len(highly_concentrated)}")
    
    print("\nTop 5 Most Concentrated Industries (with at least 10 active firms):")
    top_conc = df_final[df_final['active_firms'] >= 10].sort_values('hhi', ascending=False).head(5)
    for idx, row in top_conc.iterrows():
        print(f"- TSIC {row['tsic4']} ({row['desc_en']}): HHI = {row['hhi']:.1f}, CR4 = {row['cr4']*100:.1f}%, Revenue = THB {row['total_revenue']:,.2f}")
        
    print("\nTop 5 Largest Industries by Revenue:")
    top_rev = df_final.head(5)
    for idx, row in top_rev.iterrows():
        print(f"- TSIC {row['tsic4']} ({row['desc_en']}): Revenue = THB {row['total_revenue']:,.2f}, HHI = {row['hhi']:.1f}, Firms = {row['active_firms']}")
        
    conn.close()

if __name__ == '__main__':
    main()

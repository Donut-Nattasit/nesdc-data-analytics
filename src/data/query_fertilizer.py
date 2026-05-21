import os
import sys

def run_query():
    csv_path = "input/GTA/combined.csv"
    output_report = "output/report/thailand_fertilizer_imports_2025.md"
    output_log = "temp/fertilizer_results.txt"
    
    # Standard Middle East ISO3 country codes
    middle_east_codes = {
        'SAU': 'Saudi Arabia',
        'QAT': 'Qatar',
        'ARE': 'United Arab Emirates',
        'OMN': 'Oman',
        'KWT': 'Kuwait',
        'BHR': 'Bahrain',
        'EGY': 'Egypt',
        'IRN': 'Iran',
        'IRQ': 'Iraq',
        'ISR': 'Israel',
        'JOR': 'Jordan',
        'LBN': 'Lebanon',
        'SYR': 'Syria',
        'TUR': 'Turkey',
        'YEM': 'Yemen',
        'PSE': 'Palestine',
        'CYP': 'Cyprus'
    }
    
    print(f"Checking for input file: {csv_path}")
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found!")
        sys.exit(1)
        
    print("Parsing combined.csv line-by-line (optimized for large files)...")
    
    total_world_value = 0.0
    middle_east_value = 0.0
    partner_breakdown = {}
    
    reporter_idx = -1
    partner_idx = -1
    hs_idx = -1
    flow_idx = -1
    year_idx = -1
    value_idx = -1
    
    line_count = 0
    match_count = 0
    
    # Process line-by-line to avoid loading 4.27GB in memory
    with open(csv_path, "r", encoding="utf-8") as f:
        # Read header
        header = f.readline().strip().split(",")
        print(f"CSV Headers: {header}")
        
        # Resolve column indexes
        for idx, col in enumerate(header):
            col_lower = col.lower().strip('"')
            if col_lower == "reporter": reporter_idx = idx
            elif col_lower == "partner": partner_idx = idx
            elif col_lower == "hs_code" or col_lower == "hscode": hs_idx = idx
            elif col_lower == "flow": flow_idx = idx
            elif col_lower == "year": year_idx = idx
            elif col_lower == "value": value_idx = idx
            
        print(f"Resolved Indexes -> Reporter: {reporter_idx}, Partner: {partner_idx}, HS_Code: {hs_idx}, Flow: {flow_idx}, Year: {year_idx}, Value: {value_idx}")
        
        if -1 in (reporter_idx, partner_idx, hs_idx, flow_idx, year_idx, value_idx):
            print("Error: Could not resolve all required columns!")
            sys.exit(1)
            
        for line in f:
            line_count += 1
            if line_count % 10000000 == 0:
                print(f"Processed {line_count:,} lines...")
                
            # Parse CSV line manually to avoid overhead of csv module
            parts = line.strip().split(",")
            if len(parts) <= max(reporter_idx, partner_idx, hs_idx, flow_idx, year_idx, value_idx):
                continue
                
            # Extract fields
            reporter = parts[reporter_idx].strip('"')
            partner = parts[partner_idx].strip('"')
            hs_code = parts[hs_idx].strip('"')
            flow = parts[flow_idx].strip('"')
            year = parts[year_idx].strip('"')
            
            # Filter: Thailand, Imports, Year 2025, HS Code starting with '31' (Fertilizers)
            if reporter == "THA" and flow == "Import" and year == "2025" and hs_code.startswith("31"):
                try:
                    value = float(parts[value_idx].strip('"'))
                except ValueError:
                    continue
                    
                match_count += 1
                
                # Check for World or Region aggregates to avoid double-counting
                # Standard GTA partner for World is 'WLD' or 'World'
                if partner in ("WLD", "World", "WORLD"):
                    # We can use the WLD value directly as the total if it exists
                    # but let's also aggregate individual countries to verify
                    continue
                    
                # Exclude other region aggregates if they start with 'X' or similar (common in GTA)
                if len(partner) != 3 or not partner.isupper():
                    continue
                    
                total_world_value += value
                
                # Check if Middle East
                if partner in middle_east_codes:
                    middle_east_value += value
                    partner_breakdown[partner] = partner_breakdown.get(partner, 0.0) + value
                    
    print(f"Finished parsing. Total processed lines: {line_count:,}")
    print(f"Total matching fertilizer rows: {match_count:,}")
    
    if total_world_value == 0:
        print("Warning: Total World fertilizer import value is 0. Check data filters.")
        share = 0.0
    else:
        share = (middle_east_value / total_world_value) * 100.0
        
    print(f"Total World Fertilizer Imports: ${total_world_value:,.2f}")
    print(f"Total Middle East Fertilizer Imports: ${middle_east_value:,.2f}")
    print(f"Middle East Share: {share:.2f}%")
    
    # Sort Middle East partners by value
    sorted_partners = sorted(partner_breakdown.items(), key=lambda x: x[1], reverse=True)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_report), exist_ok=True)
    os.makedirs(os.path.dirname(output_log), exist_ok=True)
    
    # Write to text log
    with open(output_log, "w", encoding="utf-8") as lf:
        lf.write(f"Total World Fertilizer Imports: ${total_world_value:,.2f}\n")
        lf.write(f"Total Middle East Fertilizer Imports: ${middle_east_value:,.2f}\n")
        lf.write(f"Middle East Share: {share:.2f}%\n\n")
        lf.write("Middle East Partner Breakdown:\n")
        for partner, val in sorted_partners:
            partner_name = middle_east_codes.get(partner, partner)
            p_share = (val / total_world_value) * 100.0 if total_world_value > 0 else 0.0
            lf.write(f"- {partner} ({partner_name}): ${val:,.2f} ({p_share:.2f}%)\n")
            
    # Write to formal Markdown report
    with open(output_report, "w", encoding="utf-8") as rf:
        rf.write("# Thailand Fertilizer Imports Analysis (2025)\n\n")
        rf.write("## Executive Summary\n")
        rf.write("This report analyzes Thailand's import dependencies for fertilizers (HS Chapter 31) from the Middle East compared to the rest of the world for the calendar year **2025**.\n\n")
        
        rf.write("### Key Metrics Table\n")
        rf.write("| Metric | Value (USD) | Share of Total (%) |\n")
        rf.write("| :--- | :---: | :---: |\n")
        rf.write(f"| **Total World Imports** | ${total_world_value:,.2f} | 100.00% |\n")
        rf.write(f"| **Middle East Imports** | ${middle_east_value:,.2f} | **{share:.2f}%** |\n")
        rf.write(f"| Other Regions | ${(total_world_value - middle_east_value):,.2f} | {100.00 - share:.2f}% |\n\n")
        
        rf.write("## Middle East Partner Countries Breakdown (2025)\n")
        rf.write("Below is the detail of fertilizer imports to Thailand from Middle East partners, sorted by import value:\n\n")
        rf.write("| Partner Code | Country Name | Import Value (USD) | Share of World Imports (%) |\n")
        rf.write("| :---: | :--- | :---: | :---: |\n")
        for partner, val in sorted_partners:
            partner_name = middle_east_codes.get(partner, partner)
            p_share = (val / total_world_value) * 100.0 if total_world_value > 0 else 0.0
            rf.write(f"| **{partner}** | {partner_name} | ${val:,.2f} | {p_share:.2f}% |\n")
            
        rf.write("\n\n*Note: This data is compiled directly from the Global Trade Atlas (GTA) database (`combined.csv`) for HS Chapter 31 (Fertilisers).*")
        
    print(f"Report generated successfully at: {output_report}")

if __name__ == "__main__":
    run_query()

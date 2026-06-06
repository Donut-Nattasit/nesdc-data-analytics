import os
import time
import zipfile
from pathlib import Path
from datetime import datetime, timedelta

def manage_data_lifecycle():
    print("Starting Data Lifecycle Management (DLM)...")
    
    project_root = Path.cwd()
    output_dir = project_root / 'output'
    archive_dir = output_dir / 'archive'
    
    # Ensure archive directory exists
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Define 90-day TTL threshold
    threshold_date = datetime.now() - timedelta(days=90)
    threshold_timestamp = threshold_date.timestamp()
    
    print(f"Enforcing 90-day TTL. Threshold date: {threshold_date.strftime('%Y-%m-%d')}")
    
    # 1. Archive Charts (>90 days)
    chart_dir = output_dir / 'chart'
    if chart_dir.exists():
        charts_to_archive = []
        for file in chart_dir.glob('*.png'):
            if file.stat().st_mtime < threshold_timestamp:
                charts_to_archive.append(file)
                
        if charts_to_archive:
            archive_name = archive_dir / f"{datetime.now().strftime('%Y_%m')}_archived_charts.zip"
            print(f"Archiving {len(charts_to_archive)} charts to {archive_name.name}...")
            
            with zipfile.ZipFile(archive_name, 'a', zipfile.ZIP_DEFLATED) as zipf:
                for file in charts_to_archive:
                    zipf.write(file, arcname=file.name)
                    
            # Delete archived charts
            for file in charts_to_archive:
                file.unlink()
            print("Archived charts deleted from active directory.")
        else:
            print("No charts older than 90 days found.")
            
    # 2. Purge Forecasts (>90 days)
    data_dir = output_dir / 'data'
    if data_dir.exists():
        purged_forecasts = 0
        for file in data_dir.glob('*forecast*'):
            if file.stat().st_mtime < threshold_timestamp:
                file.unlink()
                purged_forecasts += 1
        print(f"Purged {purged_forecasts} transient forecast files.")
        
    # 3. Purge Models (>90 days)
    model_dir = output_dir / 'model_summary'
    if model_dir.exists():
        purged_models = 0
        for file in model_dir.glob('*.*'):
            if file.stat().st_mtime < threshold_timestamp:
                file.unlink()
                purged_models += 1
        print(f"Purged {purged_models} transient model summaries.")
        
    print("DLM complete.")

if __name__ == "__main__":
    manage_data_lifecycle()

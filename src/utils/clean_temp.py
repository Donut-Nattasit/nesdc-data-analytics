import os
import shutil
from pathlib import Path

def clean_temp_directory():
    print("Starting cleanup of the temp/ directory...")
    # Determine project root relative to this script
    # This script is at: project_root / src / utils / clean_temp.py
    project_root = Path(__file__).resolve().parent.parent.parent
    temp_dir = project_root / "temp"
    
    if not temp_dir.exists():
        print(f"Temp directory does not exist at: {temp_dir}")
        return
        
    print(f"Cleaning contents of: {temp_dir}")
    
    success_count = 0
    fail_count = 0
    
    for item in temp_dir.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
                print(f"Deleted file: {item.name}")
                success_count += 1
            elif item.is_dir():
                shutil.rmtree(item)
                print(f"Deleted directory and its contents: {item.name}")
                success_count += 1
        except Exception as e:
            print(f"Failed to delete {item.name}: {e}")
            fail_count += 1
            
    print(f"Cleanup finished. Successfully deleted: {success_count} items. Failed to delete: {fail_count} items.")

if __name__ == "__main__":
    clean_temp_directory()

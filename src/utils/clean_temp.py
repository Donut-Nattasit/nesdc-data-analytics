import os
import shutil
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Files that should never be deleted
IGNORE_FILES = {'.gitkeep', '.gitignore'}

# Optional: Only delete files older than this many seconds (e.g., 1 hour = 3600)
# Set to 0 to delete everything immediately
MAX_AGE_SECONDS = 0 

def clean_temp_directory():
    logger.info("Starting cleanup of the temp/ directory...")
    
    project_root = Path(__file__).resolve().parent.parent.parent
    temp_dir = project_root / "temp"
    
    if not temp_dir.exists():
        logger.warning(f"Temp directory does not exist at: {temp_dir}")
        return
        
    logger.info(f"Cleaning contents of: {temp_dir}")
    
    success_count = 0
    fail_count = 0
    current_time = time.time()
    
    for item in temp_dir.iterdir():
        if item.name in IGNORE_FILES:
            continue
            
        try:
            # Check file age if a threshold is set
            item_stat = item.stat()
            age_seconds = current_time - item_stat.st_mtime
            if age_seconds < MAX_AGE_SECONDS:
                continue

            if item.is_file() or item.is_symlink():
                item.unlink()
                logger.info(f"Deleted file: {item.name}")
                success_count += 1
            elif item.is_dir():
                shutil.rmtree(item)
                logger.info(f"Deleted directory: {item.name}")
                success_count += 1
                
        except PermissionError:
            logger.error(f"Permission denied: {item.name}. It may be in use by another process.")
            fail_count += 1
        except Exception as e:
            logger.error(f"Failed to delete {item.name}: {e}")
            fail_count += 1
            
    logger.info(f"Cleanup finished. Successfully deleted: {success_count} items. Failed to delete: {fail_count} items.")

if __name__ == "__main__":
    clean_temp_directory()

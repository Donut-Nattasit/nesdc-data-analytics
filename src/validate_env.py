import os
import sys
import sqlite3
from pathlib import Path
from tabulate import tabulate

# Enforce UTF-8 encoding for standard console output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def check_api_keys():
    """Verify presence and format of API keys in .env"""
    from dotenv import load_dotenv
    load_dotenv()
    
    keys = ["CEIC_API_KEY", "BOT_API_TOKEN", "EIA_API_KEY", "IMF_API_KEY"]
    results = []
    
    for key in keys:
        val = os.getenv(key)
        if not val:
            results.append([key, "Missing", "❌ Please set this in .env"])
        elif len(val) < 8:
            results.append([key, "Invalid Format", "⚠️ Value is too short to be valid"])
        else:
            masked = val[:3] + "*" * (len(val) - 6) + val[-3:] if len(val) > 6 else "***"
            results.append([key, f"Present ({masked})", "✅ Valid presence"])
            
    return results

def check_dependencies():
    """Verify that all main analytical libraries can be imported successfully."""
    libs = {
        "ceic_api_client": "ceic-api-client",
        "dotenv": "python-dotenv",
        "pandas": "pandas",
        "requests": "requests",
        "statsmodels.api": "statsmodels",
        "pmdarima": "pmdarima",
        "arch": "arch",
        "statsforecast": "statsforecast",
        "vl_convert": "vl-convert-python",
        "altair": "altair",
        "tabulate": "tabulate",
        "plotly": "plotly"
    }
    
    results = []
    for import_name, package_name in libs.items():
        try:
            __import__(import_name)
            results.append([package_name, "Available", "✅ Installed successfully"])
        except ImportError as e:
            results.append([package_name, "Unavailable", f"❌ Failed to import: {e}"])
            
    return results

def check_workspace_assets():
    """Verify folders, cache databases, and binaries are healthy and correctly positioned."""
    project_root = Path(__file__).resolve().parent.parent
    
    # Path lists
    folders = [
        "input", "output", "output/data", 
        "output/chart", "output/model_summary", "report", "assets"
    ]
    
    results = []
    
    # Check folders
    for f in folders:
        f_path = project_root / f
        if f_path.exists() and f_path.is_dir():
            results.append([f"Directory: {f}", "Found", "✅ Standard structure met"])
        else:
            results.append([f"Directory: {f}", "Not Found", "⚠️ Folder will be created dynamically on use"])
            
    # Check binary (x13as.exe)
    x13_path = project_root / "bin" / "x13as.exe"
    if x13_path.exists():
        results.append(["Binary: bin/x13as.exe", "Found", "✅ Available for seasonal adjustment"])
    else:
        results.append(["Binary: bin/x13as.exe", "Not Found", "❌ Required for X-13 ARIMA! Please download and place in bin/"])
        
    # Check API Cache DB
    db_path = project_root / "database" / "api_cache.db"
    if db_path.exists():
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_cache';")
            tbl = cursor.fetchone()
            conn.close()
            if tbl:
                results.append(["Database: api_cache.db", "Healthy", "✅ Cache table exists and is readable"])
            else:
                results.append(["Database: api_cache.db", "Needs Init", "⚠️ SQLite DB exists but table 'api_cache' not found"])
        except Exception as e:
            results.append(["Database: api_cache.db", "Corrupt", f"❌ Failed to connect: {e}"])
    else:
        results.append(["Database: api_cache.db", "Not Created Yet", "⚠️ Database file will be created on first API cache operation"])
        
    return results

def run_suite():
    print("\n" + "=" * 69)
    print("      WORKSPACE VALIDATION & DIAGNOSTIC REPORT SUITE")
    print("=" * 69)
    
    # 1. API Key Diagnostics
    print("\n[1] API Key Diagnostics:")
    api_res = check_api_keys()
    print(tabulate(api_res, headers=["Environment Key", "Status", "Details"], tablefmt="grid"))
    
    # 2. Dependency Audit
    print("\n[2] Analytical Library & Dependency Audit:")
    dep_res = check_dependencies()
    print(tabulate(dep_res, headers=["Library", "Import Status", "Details"], tablefmt="grid"))
    
    # 3. Workspace Asset Verification
    print("\n[3] Workspace Folder & Asset Health:")
    asset_res = check_workspace_assets()
    print(tabulate(asset_res, headers=["Asset Component", "Location Status", "Details"], tablefmt="grid"))
    
    # 4. Storage & Data Lifecycle Management (DLM) Audit
    print("\n[4] Data Lifecycle Management (DLM) & Storage Cleanup:")
    try:
        # Ensure project root is in path for imports
        project_root = Path(__file__).resolve().parent.parent
        if str(project_root) not in sys.path:
            sys.path.append(str(project_root))
        from src.utils.data_lifecycle import manage_data_lifecycle
        manage_data_lifecycle()
    except Exception as e:
        print(f"⚠️ Failed to run data lifecycle cleanup: {e}")
        
    print("\n" + "=" * 69)
    # Check if there are any failures
    has_failure = any("❌" in row[2] for row in api_res + dep_res + asset_res)
    if has_failure:
        print("⚠️  Diagnosis completed with some critical issues detected. Please see details above.")
        return False
    else:
        print("🎉 All systems nominal! The workspace is fully functional and optimized.")
        return True

if __name__ == "__main__":
    success = run_suite()
    sys.exit(0 if success else 1)

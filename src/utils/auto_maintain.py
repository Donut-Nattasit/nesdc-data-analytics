import sqlite3
from pathlib import Path
import sys
import os
import time

# Ensure project root is in PYTHONPATH
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

def optimize_databases():
    print("[1] Defragmenting and Optimizing SQLite Databases...")
    db_dir = project_root / "database"
    if not db_dir.exists():
        print("Database directory not found. Skipping.")
        return

    db_files = list(db_dir.rglob("*.db")) + list(db_dir.rglob("*.sqlite"))
    for db_path in db_files:
        try:
            initial_size = db_path.stat().st_size
            print(f"  -> Vacuuming {db_path.name} (Initial Size: {initial_size / (1024*1024):.2f} MB)...")
            
            # Connect and execute VACUUM and apply WAL mode permanently
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("VACUUM;")
            conn.commit()
            conn.close()
            
            final_size = db_path.stat().st_size
            saved = initial_size - final_size
            if saved > 0:
                print(f"     ✅ Saved {saved / (1024*1024):.2f} MB!")
            else:
                print(f"     ✅ Already optimal.")
        except Exception as e:
            print(f"     ❌ Failed to optimize {db_path.name}: {e}")

def run_dlm():
    print("\n[2] Running Data Lifecycle Management (DLM)...")
    try:
        from src.utils.data_lifecycle import manage_data_lifecycle
        manage_data_lifecycle()
        print("  ✅ DLM Complete.")
    except Exception as e:
        print(f"  ❌ DLM failed: {e}")

def validate_system():
    print("\n[3] Running System Diagnostics & Healing...")
    try:
        import subprocess
        venv_python = project_root / ".venv" / "Scripts" / "python.exe"
        validate_script = project_root / "src" / "validate_env.py"
        
        if venv_python.exists() and validate_script.exists():
            env = os.environ.copy()
            env["PYTHONPATH"] = str(project_root)
            
            res = subprocess.run(
                [str(venv_python), str(validate_script)],
                env=env,
                capture_output=True,
                text=True
            )
            if res.returncode == 0:
                print("  ✅ Environment is healthy and fully synced.")
            else:
                print("  ⚠️ Diagnostic warnings found:")
                lines = [l for l in res.stdout.strip().split('\n') if l]
                print('\n'.join(lines[-5:]))
        else:
            print("  ❌ Could not locate python or validate script.")
    except Exception as e:
        print(f"  ❌ Validation failed: {e}")

def main():
    print("======================================================================")
    print("         NESDC AUTONOMOUS OPTIMIZATION & MAINTENANCE DAEMON")
    print("======================================================================")
    start_time = time.time()
    
    optimize_databases()
    run_dlm()
    validate_system()
    
    duration = time.time() - start_time
    print("======================================================================")
    print(f"           MAINTENANCE COMPLETE (Duration: {duration:.1f}s)")
    print("======================================================================")

if __name__ == "__main__":
    main()

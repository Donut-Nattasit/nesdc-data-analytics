import os
import sys
import sqlite3
import argparse
from pathlib import Path
from tabulate import tabulate

# Enforce UTF-8 encoding for standard console output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_DIR = PROJECT_ROOT / "database"

def get_db_path(db_name: str) -> Path:
    """Resolve database path, checking if relative to database/ or absolute."""
    path = Path(db_name)
    if not path.is_absolute():
        # Check in DB_DIR
        db_in_dir = DB_DIR / db_name
        if db_in_dir.exists():
            return db_in_dir
        # Or relative to project root
        db_in_root = PROJECT_ROOT / db_name
        if db_in_root.exists():
            return db_in_root
    return path

def list_tables(db_path: Path):
    """List all tables in the database with row counts if possible."""
    if not db_path.exists():
        print(f"Error: Database file not found at: {db_path}", file=sys.stderr)
        sys.exit(1)
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        
        results = []
        for t in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM `{t}`")
                count = cursor.fetchone()[0]
                results.append([t, count])
            except Exception:
                results.append([t, "N/A"])
                
        conn.close()
        
        print(f"\n📁 Database: {db_path.name}")
        print(tabulate(results, headers=["Table Name", "Estimated Row Count"], tablefmt="grid"))
    except Exception as e:
        print(f"Error reading database: {e}", file=sys.stderr)
        sys.exit(1)

def show_schema(db_path: Path, table_name: str = None):
    """Show schemas for tables or a specific table."""
    if not db_path.exists():
        print(f"Error: Database file not found at: {db_path}", file=sys.stderr)
        sys.exit(1)
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if table_name:
            cursor.execute(f"PRAGMA table_info(`{table_name}`);")
            columns = cursor.fetchall()
            if not columns:
                print(f"Error: Table '{table_name}' not found in database {db_path.name}", file=sys.stderr)
                conn.close()
                sys.exit(1)
            
            headers = ["CID", "Column Name", "Type", "NotNull", "Default Value", "Primary Key"]
            print(f"\n📋 Table Schema: `{table_name}` in {db_path.name}")
            print(tabulate(columns, headers=headers, tablefmt="grid"))
        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [row[0] for row in cursor.fetchall()]
            
            for t in tables:
                cursor.execute(f"PRAGMA table_info(`{t}`);")
                columns = cursor.fetchall()
                print(f"\n📋 Table Schema: `{t}`")
                headers = ["CID", "Column Name", "Type", "NotNull", "Default Value", "Primary Key"]
                print(tabulate(columns, headers=headers, tablefmt="grid"))
                
        conn.close()
    except Exception as e:
        print(f"Error reading schema: {e}", file=sys.stderr)
        sys.exit(1)

def preview_table(db_path: Path, table_name: str, limit: int = 10):
    """Safe table preview with strict limit check."""
    if not db_path.exists():
        print(f"Error: Database file not found at: {db_path}", file=sys.stderr)
        sys.exit(1)
        
    # Cap limit to prevent token flood
    limit = min(max(1, limit), 100)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verify table exists to prevent SQL injection
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?;", (table_name,))
        if not cursor.fetchone():
            print(f"Error: Table '{table_name}' not found.", file=sys.stderr)
            conn.close()
            sys.exit(1)
            
        cursor.execute(f"SELECT * FROM `{table_name}` LIMIT {limit};")
        rows = cursor.fetchall()
        
        cursor.execute(f"PRAGMA table_info(`{table_name}`);")
        headers = [col[1] for col in cursor.fetchall()]
        
        conn.close()
        
        print(f"\n👁️ Preview of table `{table_name}` in {db_path.name} (Limit {limit}):")
        if not rows:
            print("No rows found in table.")
        else:
            print(tabulate(rows, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"Error previewing table: {e}", file=sys.stderr)
        sys.exit(1)

def execute_safe_query(db_path: Path, query: str):
    """Execute a read-only query safely by enforcing limit and read-only check."""
    if not db_path.exists():
        print(f"Error: Database file not found at: {db_path}", file=sys.stderr)
        sys.exit(1)
        
    query_stripped = query.strip().upper()
    
    # Block writing operations
    write_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "REPLACE", "TRUNCATE"]
    if any(kw in query_stripped for kw in write_keywords):
        print("Error: For safety, write queries (INSERT, UPDATE, DELETE, etc.) are blocked in this explorer.", file=sys.stderr)
        sys.exit(1)
        
    if not query_stripped.startswith("SELECT") and not query_stripped.startswith("PRAGMA") and not query_stripped.startswith("EXPLAIN"):
        print("Error: Query must start with SELECT, PRAGMA, or EXPLAIN.", file=sys.stderr)
        sys.exit(1)
        
    # Enforce limit if it is SELECT and doesn't contain LIMIT
    if "SELECT" in query_stripped and "LIMIT" not in query_stripped:
        query = f"{query.rstrip(';')} LIMIT 20"
        print("ℹ️ Note: Automatically appended LIMIT 20 to select query to prevent output bloat.")
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Try to extract description/column headers
        headers = [desc[0] for desc in cursor.description] if cursor.description else []
        
        conn.close()
        
        print(f"\n🔍 Query Output from {db_path.name}:")
        if not rows:
            print("Query executed successfully. No rows returned.")
        else:
            print(tabulate(rows, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"Database Query Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Safe SQLite Database Explorer CLI")
    parser.add_argument("--db", required=True, help="Database filename in './database/' (e.g. GTA.db, DBD.db) or direct path")
    
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")
    
    # tables subcommand
    subparsers.add_parser("tables", help="List all tables in the database")
    
    # schema subcommand
    schema_parser = subparsers.add_parser("schema", help="Show table column structure")
    schema_parser.add_argument("--table", help="Specific table name (optional)")
    
    # preview subcommand
    preview_parser = subparsers.add_parser("preview", help="Preview table rows safely")
    preview_parser.add_argument("--table", required=True, help="Table name")
    preview_parser.add_argument("--limit", type=int, default=10, help="Row limit (max 100, default 10)")
    
    # query subcommand
    query_parser = subparsers.add_parser("query", help="Run a read-only query safely")
    query_parser.add_argument("--sql", required=True, help="SQL select statement")
    
    args = parser.parse_args()
    db_path = get_db_path(args.db)
    
    if args.command == "tables":
        list_tables(db_path)
    elif args.command == "schema":
        show_schema(db_path, args.table)
    elif args.command == "preview":
        preview_table(db_path, args.table, args.limit)
    elif args.command == "query":
        execute_safe_query(db_path, args.sql)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

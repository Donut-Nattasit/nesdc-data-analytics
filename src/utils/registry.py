import os
import json
from pathlib import Path
from datetime import datetime

# Define standard paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = PROJECT_ROOT / 'database' / 'PROJECT_STATE.json'

def load_registry() -> dict:
    """Load the JSON registry, initializing it if it doesn't exist."""
    if not JSON_PATH.exists():
        # Initialize default empty registry structure
        default_registry = {
            "datasets": [],
            "models": [],
            "visualizations": [],
            "reports": []
        }
        JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        save_registry(default_registry)
        return default_registry
    
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Fallback if file is corrupted
            return {
                "datasets": [],
                "models": [],
                "visualizations": [],
                "reports": []
            }

def save_registry(registry: dict):
    """Save the registry to the JSON file."""
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def add_dataset(series_id, source, raw_path="", transformed_path="", forecast_path="", status="Ready", last_update=None):
    """Programmatic API to register or update a dataset."""
    if not last_update:
        last_update = datetime.now().strftime('%Y-%m-%d')
    
    registry = load_registry()
        
    # Check if dataset already exists to update it, otherwise append
    exists = False
    for d in registry.get("datasets", []):
        if d.get("series_id") == series_id:
            d.update({
                "source": source,
                "raw_path": raw_path or d.get("raw_path", ""),
                "transformed_path": transformed_path or d.get("transformed_path", ""),
                "forecast_path": forecast_path or d.get("forecast_path", ""),
                "status": status,
                "last_update": last_update
            })
            exists = True
            break
            
    if not exists:
        if "datasets" not in registry:
            registry["datasets"] = []
        registry["datasets"].append({
            "series_id": series_id,
            "source": source,
            "raw_path": raw_path,
            "transformed_path": transformed_path,
            "forecast_path": forecast_path,
            "status": status,
            "last_update": last_update
        })
        
    save_registry(registry)
    print(f"Dataset '{series_id}' registered successfully in PROJECT_STATE.json.")

def add_model(name, model_type, source_data, summary_path, status="Finalized", last_update=None):
    """Programmatic API to register or update a model."""
    if not last_update:
        last_update = datetime.now().strftime('%Y-%m-%d')
        
    registry = load_registry()
        
    exists = False
    for m in registry.get("models", []):
        if m.get("name") == name:
            m.update({
                "type": model_type,
                "source_data": source_data,
                "summary_path": summary_path,
                "status": status,
                "last_update": last_update
            })
            exists = True
            break
            
    if not exists:
        if "models" not in registry:
            registry["models"] = []
        registry["models"].append({
            "name": name,
            "type": model_type,
            "source_data": source_data,
            "summary_path": summary_path,
            "status": status,
            "last_update": last_update
        })
        
    save_registry(registry)
    print(f"Model '{name}' registered successfully in PROJECT_STATE.json.")

def add_visualization(name, chart_type, source_data, png_path, status="Rendered", last_update=None):
    """Programmatic API to register or update a visualization."""
    if not last_update:
        last_update = datetime.now().strftime('%Y-%m-%d')
        
    registry = load_registry()
        
    exists = False
    for v in registry.get("visualizations", []):
        if v.get("name") == name:
            v.update({
                "type": chart_type,
                "source_data": source_data,
                "png_path": png_path,
                "status": status,
                "last_update": last_update
            })
            exists = True
            break
            
    if not exists:
        if "visualizations" not in registry:
            registry["visualizations"] = []
        registry["visualizations"].append({
            "name": name,
            "type": chart_type,
            "source_data": source_data,
            "png_path": png_path,
            "status": status,
            "last_update": last_update
        })
        
    save_registry(registry)
    print(f"Visualization '{name}' registered successfully in PROJECT_STATE.json.")

def add_report(title, author, path, date=None, status="Published"):
    """Programmatic API to register or update a formal report."""
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
        
    registry = load_registry()
        
    exists = False
    for r in registry.get("reports", []):
        if r.get("title") == title:
            r.update({
                "author": author,
                "date": date,
                "path": path,
                "status": status
            })
            exists = True
            break
            
    if not exists:
        if "reports" not in registry:
            registry["reports"] = []
        registry["reports"].append({
            "title": title,
            "author": author,
            "date": date,
            "path": path,
            "status": status
        })
        
    save_registry(registry)
    print(f"Report '{title}' registered successfully in PROJECT_STATE.json.")

# Kept for backward compatibility if any external legacy process calls sync/init
def generate_markdown_from_json():
    """No-op for backward compatibility. Markdown view is deprecated."""
    pass

def parse_markdown_to_json():
    """No-op for backward compatibility. Markdown view is deprecated."""
    pass

if __name__ == "__main__":
    import sys
    # Initialize registry file if it doesn't exist
    load_registry()
    print("PROJECT_STATE.json is active and up to date.")

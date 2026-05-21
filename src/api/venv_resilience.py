import os
import sys
import re
import getpass
from pathlib import Path

def repair_pyvenv_cfg():
    """
    Detect username mismatches in pyvenv.cfg and repair them dynamically.
    Enables zero-error multi-machine execution over OneDrive sync.
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    cfg_path = project_root / ".venv" / "pyvenv.cfg"
    
    if not cfg_path.exists():
        print(f"[Venv Resilience] pyvenv.cfg not found at: {cfg_path}")
        return False
        
    print(f"[Venv Resilience] Auditing pyvenv.cfg at: {cfg_path}")
    
    # Get current username
    current_username = getpass.getuser()
    print(f"[Venv Resilience] Current system username: {current_username}")
    
    with open(cfg_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Regex to match C:\Users\<Username> or C:/Users/<Username> patterns
    pattern = r"([cC]:[/\\][uU]sers[/\\])([^/\\]+)"
    
    def replace_user(match):
        prefix = match.group(1)
        old_user = match.group(2)
        if old_user.lower() != current_username.lower():
            print(f"[Venv Resilience] Mismatch detected: Replacing '{old_user}' with '{current_username}'")
            # Enforce consistent backslash separation for Windows paths
            clean_prefix = prefix.replace('/', '\\')
            return f"{clean_prefix}{current_username}"
        return match.group(0)
        
    new_content, count = re.subn(pattern, replace_user, content)
    
    if count > 0:
        with open(cfg_path, 'w', encoding='utf-8', newline='\r\n') as f:
            f.write(new_content)
        print(f"[Venv Resilience] Successfully updated {count} path references in pyvenv.cfg!")
        return True
    else:
        print("[Venv Resilience] Path references in pyvenv.cfg are already correct and matching.")
        return True

if __name__ == "__main__":
    success = repair_pyvenv_cfg()
    sys.exit(0 if success else 1)

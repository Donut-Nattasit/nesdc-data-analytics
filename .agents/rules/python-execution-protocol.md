---
trigger: always_on
glob: "*.py"
description: Execute Python processes correctly using the local virtual environment and PYTHONPATH.
---

# Python Execution Protocol

To avoid module import conflicts and guarantee that the local virtual environment dependencies are always used correctly, execute all Python processes using the following template:

* **Interpreter Path**: `.\.venv\Scripts\python.exe` (relative from workspace root).
* **Python Path**: Set the environment variable `PYTHONPATH` to `.` (the current directory) so modular imports (e.g., `from src.api.bot_client import BOTClient`) resolve flawlessly.
* **Unified PowerShell Template**:
  ```powershell
  powershell -Command "$env:PYTHONPATH='.'; .\.venv\Scripts\python.exe path/to/script.py"
  ```

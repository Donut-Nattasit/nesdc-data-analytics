---
trigger: always_on
glob: "*"
description: Never hardcode absolute paths and resolve file paths dynamically relative to the project root.
---

# Zero Absolute Paths

* Never hardcode absolute paths (e.g., `C:\Users\natta\...`).
* Always resolve file paths dynamically relative to the project root. In Python, utilize `pathlib.Path.cwd()` or `pathlib.Path(__file__).parent` references.

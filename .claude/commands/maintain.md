# Maintain

Run workspace maintenance: database optimization, temp cleanup, environment validation, and status dashboard generation.

**Execute in sequence:**

1. Clean temp directory:

```powershell
& '.venv\Scripts\python.exe' 'src\utils\clean_temp.py'
```

2. Run database VACUUM + generate `WORKSPACE_STATUS.md`:

```powershell
& '.venv\Scripts\python.exe' 'src\utils\auto_maintain.py'
```

3. Validate environment:

```powershell
& '.venv\Scripts\python.exe' 'src\validate_env.py'
```

**Report back:** Show the contents of the generated `WORKSPACE_STATUS.md` (pipeline last-run dates, registry counts, loose file tally). Flag any environment warnings.

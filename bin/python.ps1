# bin/python.ps1
# Workspace-specific Python wrapper that dynamically repairs the virtual environment (venv) configuration
# before execution to resolve username mismatches caused by OneDrive synchronization.
# Usage: .\bin\python.ps1 [script.py] [args...]

$env:PYTHONPATH = "."
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"


# Self-healing: Repair .venv/pyvenv.cfg if username mismatch exists (OneDrive sync resilience)
$possibleCfgPaths = @(
    (Join-Path $PSScriptRoot "..\.venv\pyvenv.cfg"),
    (Join-Path (Get-Location) ".venv\pyvenv.cfg")
)
foreach ($path in $possibleCfgPaths) {
    if (Test-Path $path) {
        $cfgFile = [System.IO.Path]::GetFullPath($path)
        $content = Get-Content $cfgFile -Raw
        $currentUser = $env:USERNAME
        $newContent = $content -replace "([cC]:[/\\][uU]sers[/\\])([^/\\]+)", "`$1$currentUser"
        if ($content -ne $newContent) {
            Set-Content $cfgFile $newContent -NoNewline
            Write-Host "[Venv Resilience] Repaired virtual environment path in $cfgFile for user: $currentUser" -ForegroundColor Green
        }
        break
    }
}

# Find the virtual environment python executor
$possiblePythonExecs = @(
    (Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"),
    (Join-Path (Get-Location) ".venv\Scripts\python.exe")
)
$PythonExec = $null
foreach ($exec in $possiblePythonExecs) {
    if (Test-Path $exec) {
        $PythonExec = [System.IO.Path]::GetFullPath($exec)
        break
    }
}

if (-not $PythonExec) {
    Write-Error "Virtual environment python executor not found at .venv/Scripts/python.exe."
    Write-Host "Please ensure you have initialized a virtual environment under .venv" -ForegroundColor Yellow
    Exit 1
}

# Run the command passing through all original arguments
& $PythonExec $args
Exit $LASTEXITCODE

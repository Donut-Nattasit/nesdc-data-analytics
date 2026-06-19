# bin/python.ps1
# Central Python launcher for this workspace.
#
# The virtual environment lives OUTSIDE OneDrive (in %LOCALAPPDATA%) so it is never
# synced between machines. Each laptop builds its own native venv via setup.ps1, which
# means there is no foreign username in pyvenv.cfg to "repair" -- the old class of
# OneDrive path errors is gone by construction.
#
# Usage:  .\bin\python.ps1 [script.py] [args...]   (run from the project root)

$env:PYTHONPATH = "."
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

# Resolve the venv python. Primary: local-only venv outside OneDrive.
# Fallback: legacy in-project .venv, in case an old machine hasn't run setup.ps1 yet.
$candidates = @(
    (Join-Path $env:LOCALAPPDATA "venvs\data-analysis\Scripts\python.exe"),
    (Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"),
    (Join-Path (Get-Location) ".venv\Scripts\python.exe")
)

$PythonExec = $null
foreach ($exec in $candidates) {
    if (Test-Path $exec) {
        $PythonExec = [System.IO.Path]::GetFullPath($exec)
        break
    }
}

if (-not $PythonExec) {
    Write-Error "Python virtual environment not found."
    Write-Host  "Run setup.ps1 from the project root to build it on this machine." -ForegroundColor Yellow
    Exit 1
}

& $PythonExec $args
Exit $LASTEXITCODE

# setup.ps1 -- run once per machine to build this workspace's Python environment.
#
# WHY THIS DESIGN:
#   The project folder syncs across machines via OneDrive. A virtual environment must
#   NOT sync: it contains 100,000+ files (slow sync) and machine-specific absolute
#   paths in pyvenv.cfg / Scripts (the recurring "path error" when switching laptops).
#
#   So the venv lives OUTSIDE OneDrive, in %LOCALAPPDATA%\venvs\data-analysis. Each
#   machine builds its own. Nothing venv-related sits inside the synced folder -- no
#   real folder, no junction, no symlink. Scripts reach it via bin\python.ps1.
#
# Run:  .\setup.ps1          (build / update the environment)
#       .\setup.ps1 -Force   (delete and rebuild from scratch)

param(
    [switch]$Force
)

$ErrorActionPreference = 'Continue'
$ProjectRoot   = $PSScriptRoot
$VenvDir       = "$env:LOCALAPPDATA\venvs\data-analysis"
$VenvPython    = "$VenvDir\Scripts\python.exe"

# --- 1. Find Python 3.12 ---
$PythonLauncher = $null
$PythonVer = ''
foreach ($candidate in @('py -3.12', 'python3.12', 'python')) {
    try {
        $ver = & cmd /c "$candidate --version 2>&1"
        if ($ver -match '3\.12') { $PythonLauncher = $candidate; $PythonVer = $ver; break }
    } catch {}
}
if (-not $PythonLauncher) {
    Write-Error 'Python 3.12 not found. Install it from https://python.org and ensure it is on PATH, then re-run.'
    exit 1
}
Write-Host "Using Python: $PythonLauncher ($PythonVer)"

# --- 2. (Optional) wipe for a clean rebuild ---
if ($Force) {
    Write-Host "Removing existing venv at $VenvDir ..."
    Remove-Item -Recurse -Force $VenvDir -ErrorAction SilentlyContinue
}

# --- 3. Create the venv (outside OneDrive) ---
if (-not (Test-Path $VenvPython)) {
    Write-Host "Creating virtual environment at $VenvDir ..."
    & cmd /c "$PythonLauncher -m venv `"$VenvDir`""
    if (-not (Test-Path $VenvPython)) { Write-Error 'venv creation failed.'; exit 1 }
} else {
    Write-Host "Virtual environment already exists at $VenvDir"
}

# --- 4. Safety: make sure no .venv is lingering inside OneDrive ---
$StaleVenv = Join-Path $ProjectRoot '.venv'
if (Test-Path $StaleVenv) {
    Write-Host "Removing stale .venv inside the OneDrive folder (it must not live here)..." -ForegroundColor Yellow
    # rmdir removes a junction without touching its target; -Recurse handles a real folder.
    cmd /c "rmdir /S /Q `"$StaleVenv`"" 2>$null
    if (Test-Path $StaleVenv) { Remove-Item -Recurse -Force $StaleVenv -ErrorAction SilentlyContinue }
}

# --- 4b. Reconstruct the workspace directory scaffold ---
# output/, report/, database/, input/ are gitignored, so a fresh clone is missing
# them. Pipelines self-create per-pipeline subdirs at runtime; here we lay down the
# top-level structure so the workspace matches a fully-populated checkout.
$Scaffold = @(
    'temp', 'to_do_list', 'input', 'report', 'database',
    'output', 'output\chart', 'output\data', 'output\model_summary', 'output\archive'
)
foreach ($Dir in $Scaffold) {
    $DirPath = Join-Path $ProjectRoot $Dir
    if (-not (Test-Path $DirPath)) { New-Item -ItemType Directory -Path $DirPath | Out-Null }
}

# --- 5. Install dependencies ---
Write-Host ''
Write-Host 'Installing packages (first run may take a few minutes)...'
& $VenvPython -m pip install --upgrade pip -q
& $VenvPython -m pip install -r "$ProjectRoot\requirements.txt" --find-links "$ProjectRoot\wheels"
if ($LASTEXITCODE -ne 0) { Write-Error 'pip install failed.'; exit 1 }

# --- 6. Persist PYTHONPATH for terminal sessions ---
$Current = [Environment]::GetEnvironmentVariable('PYTHONPATH', 'User')
if ($Current -ne $ProjectRoot) {
    [Environment]::SetEnvironmentVariable('PYTHONPATH', $ProjectRoot, 'User')
    Write-Host ''
    Write-Host "PYTHONPATH set to $ProjectRoot (restart your terminal for it to take effect)."
}

Write-Host ''
Write-Host 'Done. This machine is ready.' -ForegroundColor Green
Write-Host 'Run scripts via:  .\bin\python.ps1 <script.py>'
& $VenvPython -c "import sys; print('venv python ->', sys.executable)"

# Bootstrap script -- run once per machine to set up the Python environment.
#
# WHY: .venv stored inside OneDrive causes two problems:
#   1. OneDrive syncs 100,000+ small package files between machines (very slow)
#   2. Venv activation scripts contain absolute paths that break if usernames differ
#
# SOLUTION: Store the real venv in %LOCALAPPDATA% (never synced), then create a
# junction at .venv inside the project so all scripts that call .venv\Scripts\python
# continue to work unchanged. OneDrive does not follow junctions.

param(
    [switch]$Force
)

$ErrorActionPreference = 'Continue'
$ProjectRoot = $PSScriptRoot
$LocalVenvPath = "$env:LOCALAPPDATA\venvs\data-analysis"
$JunctionPath = Join-Path $ProjectRoot '.venv'

# --- Find Python 3.12 ---
$PythonExe = $null
$PythonVer = ''
foreach ($candidate in @('py -3.12', 'python3.12', 'python')) {
    try {
        $ver = & cmd /c "$candidate --version 2>&1"
        if ($ver -match '3\.12') {
            $PythonExe = $candidate
            $PythonVer = $ver
            break
        }
    } catch {}
}
if (-not $PythonExe) {
    Write-Error 'Python 3.12 not found. Install from https://python.org and ensure it is in PATH.'
    exit 1
}
Write-Host "Using Python: $PythonExe ($PythonVer)"

# --- Remove old venv if -Force ---
if ($Force) {
    Write-Host "Removing existing venv at $LocalVenvPath ..."
    Remove-Item -Recurse -Force $LocalVenvPath -ErrorAction SilentlyContinue
    if (Test-Path $JunctionPath) {
        cmd /c "rmdir `"$JunctionPath`""
    }
}

# --- Create venv ---
if (-not (Test-Path "$LocalVenvPath\Scripts\python.exe")) {
    Write-Host "Creating virtual environment at $LocalVenvPath ..."
    & cmd /c "$PythonExe -m venv `"$LocalVenvPath`""
    if ($LASTEXITCODE -ne 0) {
        Write-Error 'venv creation failed.'
        exit 1
    }
} else {
    Write-Host "Virtual environment already exists at $LocalVenvPath"
}

# --- Create junction .venv -> local venv ---
# If .venv is a real directory (old OneDrive setup), remove it first.
if (Test-Path $JunctionPath) {
    $item = Get-Item $JunctionPath -Force
    if ($item.LinkType -ne 'Junction') {
        Write-Host '.venv is a real directory (old OneDrive setup). Removing to replace with junction...'
        Write-Host '  Packages are safe -- they will be reinstalled from requirements.txt.'
        Remove-Item -Recurse -Force $JunctionPath
    }
}
if (-not (Test-Path $JunctionPath)) {
    Write-Host "Creating junction .venv -> $LocalVenvPath ..."
    cmd /c "mklink /J `"$JunctionPath`" `"$LocalVenvPath`""
} else {
    Write-Host '.venv junction already in place'
}

# --- Install dependencies ---
Write-Host ''
Write-Host 'Installing packages (this may take a few minutes on first run)...'
& "$JunctionPath\Scripts\pip" install --upgrade pip -q
& "$JunctionPath\Scripts\pip" install -r "$ProjectRoot\requirements.txt" --find-links "$ProjectRoot\wheels"
if ($LASTEXITCODE -ne 0) {
    Write-Error 'pip install failed.'
    exit 1
}

# --- Set PYTHONPATH user env var ---
$Current = [Environment]::GetEnvironmentVariable('PYTHONPATH', 'User')
if ($Current -ne $ProjectRoot) {
    [Environment]::SetEnvironmentVariable('PYTHONPATH', $ProjectRoot, 'User')
    Write-Host ''
    Write-Host "PYTHONPATH set to $ProjectRoot"
    Write-Host 'Restart your terminal for this to take effect.'
}

Write-Host ''
Write-Host 'Done. Verify with:'
Write-Host '  .venv\Scripts\python.exe -c "import sys; print(sys.executable)"'

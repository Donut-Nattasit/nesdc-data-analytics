Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "      NESDC Data Analysis Workspace Setup Wizard" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "Welcome! This wizard will build your local sandbox and configure your data access."
Write-Host ""

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."

# Step 1: Virtual Environment
Write-Host "[1/5] Building the Python sandbox (.venv)..." -ForegroundColor Yellow
if (-Not (Test-Path "$ProjectRoot\.venv")) {
    python -m venv "$ProjectRoot\.venv"
    if ($?) {
        Write-Host "  -> Sandbox created successfully." -ForegroundColor Green
    } else {
        Write-Host "  -> Error: Python is not installed or not in your system PATH." -ForegroundColor Red
        Write-Host "  -> Please install Python 3.10+ and try again." -ForegroundColor Red
        Exit
    }
} else {
    Write-Host "  -> Sandbox already exists. Skipping." -ForegroundColor Green
}

# Step 2: Initialize Workspace Directories
Write-Host "`n[2/5] Initializing Workspace Directories..." -ForegroundColor Yellow
$Directories = @(
    "temp",
    "to_do_list",
    "report",
    "database",
    "output",
    "output\chart",
    "output\data",
    "output\model_summary",
    "output\archive"
)
foreach ($Dir in $Directories) {
    $DirPath = Join-Path -Path $ProjectRoot -ChildPath $Dir
    if (-Not (Test-Path $DirPath)) {
        New-Item -ItemType Directory -Path $DirPath | Out-Null
    }
}
Write-Host "  -> Directories initialized." -ForegroundColor Green

# Step 3: Install Requirements
Write-Host "`n[3/5] Installing Economist Tools (this may take a few minutes)..." -ForegroundColor Yellow
$PythonExe = "$ProjectRoot\.venv\Scripts\python.exe"
& $PythonExe -m pip install --upgrade pip --quiet
& $PythonExe -m pip install -r "$ProjectRoot\requirements.txt" --quiet
Write-Host "  -> Tools installed successfully." -ForegroundColor Green

# Step 4: API Keys (.env)
Write-Host "`n[4/5] Configuring Data Access Passwords..." -ForegroundColor Yellow
$EnvPath = "$ProjectRoot\.env"

if (-Not (Test-Path $EnvPath)) {
    Write-Host "We need your API keys so the AI can download data automatically."
    Write-Host "If you don't have a key right now, just press Enter to skip." -ForegroundColor Gray
    
    $CEIC_KEY = Read-Host "  Please paste your CEIC API Key"
    $BOT_KEY = Read-Host "  Please paste your Bank of Thailand API Key"
    $EIA_KEY = Read-Host "  Please paste your EIA API Key"
    
    $EnvContent = @"
# CEIC World Trend Plus
CEIC_API_KEY=$CEIC_KEY

# Bank of Thailand (BOT) API
BOT_API_KEY=$BOT_KEY

# U.S. Energy Information Administration (EIA)
EIA_API_KEY=$EIA_KEY

# OpenAI / AI Agent Keys (if applicable)
OPENAI_API_KEY=
"@
    Set-Content -Path $EnvPath -Value $EnvContent
    Write-Host "  -> Secrets saved safely to the .env file." -ForegroundColor Green
} else {
    Write-Host "  -> Secrets file (.env) already exists. Skipping." -ForegroundColor Green
}

# Step 5: Diagnostics
Write-Host "`n[5/5] Running Final Health Check..." -ForegroundColor Yellow
$env:PYTHONPATH=$ProjectRoot
& $PythonExe "$ProjectRoot\src\validate_env.py"

Write-Host "`n=========================================================" -ForegroundColor Cyan
Write-Host "Setup Complete! You are fully ready to analyze data." -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Cyan

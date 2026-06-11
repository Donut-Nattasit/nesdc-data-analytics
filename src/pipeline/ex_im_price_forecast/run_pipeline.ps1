# NESDC Export & Import Price Analysis - Monthly Pipeline Runner
# This PowerShell script runs the complete pipeline: data retrieval, forecasting, visualization, and report compilation.
# Ensure you run this from the project root directory.

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Starting NESDC Export & Import Price Pipeline..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Set PYTHONPATH to project root to resolve modules correctly
$env:PYTHONPATH = "..\..\.."

# Self-healing: Repair .venv/pyvenv.cfg if username mismatch exists (OneDrive sync resilience)
$possibleCfgPaths = @(
    (Join-Path $PSScriptRoot "..\..\..\.venv\pyvenv.cfg"),
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

# Define paths
$PythonExec = "..\..\..\.venv\Scripts\python.exe"
$Orchestrator = "orchestrator.py"

if (-not (Test-Path $PythonExec)) {
    Write-Error "Virtual environment python executor not found at $PythonExec"
    Write-Host "Please ensure you have set up the virtual environment by running: python -m venv .venv" -ForegroundColor Yellow
    Exit 1
}

# Run the master pipeline orchestrator
Write-Host "Running master pipeline orchestrator..." -ForegroundColor Green
& $PythonExec $Orchestrator

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Monthly Pipeline failed to execute successfully." -ForegroundColor Red
    Exit $LASTEXITCODE
} else {
    Write-Host "==========================================================" -ForegroundColor Green
    Write-Host "🎉 Monthly Pipeline completed successfully!" -ForegroundColor Green
    Write-Host "Special Economic Brief saved at: report/ex_im_price_forecast/ex_im_price_forecast.md" -ForegroundColor Green
    Write-Host "Visual charts updated at: output/chart/ex_im_price_forecast/" -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Green
}

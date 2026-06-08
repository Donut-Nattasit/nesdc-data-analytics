# NESDC Dubai Crude Oil Analysis - Monthly Pipeline Runner
# This PowerShell script runs the complete pipeline: data retrieval, forecasting, visualization, and report compilation.
# Ensure you run this from the project root directory.

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Starting NESDC Dubai Oil Analysis Monthly Pipeline..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

Write-Host "`n⚠️  WAIT! Have you updated the local data? ⚠️" -ForegroundColor Yellow
Write-Host "Please ensure you have updated the input data in:" -ForegroundColor Yellow
Write-Host "-> input/projects/dubai_oil/dubai_price.xlsx" -ForegroundColor White
Read-Host "Press Enter to continue or Ctrl+C to abort"
# Set PYTHONPATH to project root to resolve modules correctly
$env:PYTHONPATH = "..\..\.."

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
    $CurrentYyyyMm = Get-Date -Format "yyyy-MM"
    Write-Host "Special Economic Report saved at: report/energy_price_forecast/energy_price_forecast.md" -ForegroundColor Green
    Write-Host "Visual charts updated at: output/chart/" -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Green
}

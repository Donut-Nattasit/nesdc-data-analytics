# NESDC Prepared Food CPI Shock Pipeline Runner
# Usage: .\src\pipeline\prepared_food_shock\run_pipeline.ps1

$env:PYTHONPATH='.'
$env:PYTHONUTF8='1'

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  Starting Prepared Food CPI Shock Pipeline Execution" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

Write-Host "`n>>> Running Simulation & Analytical Model..." -ForegroundColor Cyan
.\bin\python.ps1 src/pipeline/prepared_food_shock/run_analysis.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERROR] Simulation failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n>>> Generating Analytical Report..." -ForegroundColor Cyan
.\bin\python.ps1 src/pipeline/prepared_food_shock/generate_report.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERROR] Report generation failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "  Pipeline execution completed successfully!" -ForegroundColor Green
Write-Host "  Primary Report: report\prepared_food_shock\prepared_food_shock.md" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

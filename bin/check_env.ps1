# PowerShell script to verify environment and repair path settings in .venv/pyvenv.cfg
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Workspace Environment Quality Check" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

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
        } else {
            Write-Host "[Venv Resilience] Virtual environment path is already correct." -ForegroundColor Green
        }
        break
    }
}


# 2. Verify venv works now and list main packages
Write-Host ""
Write-Host "Checking virtual environment packages..." -ForegroundColor Yellow
$VenvPython = "$env:LOCALAPPDATA\venvs\data-analysis\Scripts\python.exe"
if (Test-Path $VenvPython) {
    $env:PYTHONPATH="."
    & $VenvPython -m pip list | Select-String -Pattern "ceic-api-client|altair|statsforecast|statsmodels|scikit-learn|tabulate|vl-convert"
    Write-Host "Environment validation complete. The virtual environment is ready!" -ForegroundColor Green
} else {
    Write-Error "Virtual environment not found. Run setup.ps1 to build it on this machine."
}

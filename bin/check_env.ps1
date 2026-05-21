# PowerShell script to verify environment and repair path settings in .venv/pyvenv.cfg
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Workspace Environment Quality Check" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Run venv resilience check using system Python
$pythonCmd = "python"
try {
    # Test if 'python' works in the path
    $null = Get-Command python -ErrorAction Stop
} catch {
    # If python is not found, try typical AppData location
    $userProfile = $env:USERPROFILE
    $localPython = Join-Path $userProfile "AppData\Local\Programs\Python\Python312\python.exe"
    if (Test-Path $localPython) {
        $pythonCmd = $localPython
    } else {
        # Search for any python.exe under AppData
        $found = Get-ChildItem -Path (Join-Path $userProfile "AppData\Local\Programs\Python") -Filter "python.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            $pythonCmd = $found.FullName
        } else {
            Write-Warning "Could not find global python.exe to run resilience script. Attempting to use virtual environment's python directly..."
            $pythonCmd = ".\.venv\Scripts\python.exe"
        }
    }
}

Write-Host "Running venv resilience script with: $pythonCmd"
& $pythonCmd src/api/venv_resilience.py

# 2. Verify venv works now and list main packages
Write-Host ""
Write-Host "Checking virtual environment packages..." -ForegroundColor Yellow
if (Test-Path ".\.venv\Scripts\python.exe") {
    $env:PYTHONPATH="."
    & .\.venv\Scripts\python.exe -m pip list | Select-String -Pattern "ceic-api-client|altair|statsforecast|statsmodels|scikit-learn|tabulate|vl-convert"
    Write-Host "Environment validation complete. The virtual environment is ready!" -ForegroundColor Green
} else {
    Write-Error "Virtual environment not found at .\.venv"
}

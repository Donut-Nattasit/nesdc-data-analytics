# Registers the auto_maintain.py script as a Windows Scheduled Task
# This runs silently in the background every Sunday at 3:00 AM

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
$PythonExe = "$env:LOCALAPPDATA\venvs\data-analysis\Scripts\python.exe"
$ScriptPath = "$ProjectRoot\src\utils\auto_maintain.py"

if (-Not (Test-Path $PythonExe)) {
    Write-Host "Error: Cannot find python.exe. Have you created the .venv?" -ForegroundColor Red
    Pause
    Exit
}

Write-Host "Installing NESDC Autonomous Maintenance Task..." -ForegroundColor Cyan

# Create Task Action (Run hidden PowerShell that invokes the python script)
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -Command `"& '$PythonExe' '$ScriptPath'`""

# Trigger: Weekly on Sunday at 3:00 AM
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3:00AM

# Settings: Run as soon as possible if missed (StartWhenAvailable)
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

$TaskName = "NESDC_Workspace_Optimizer"

try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Runs weekly defragmentation and optimization for NESDC Data Analysis Workspace" -Force | Out-Null
    Write-Host "✅ Successfully installed scheduled task: '$TaskName'" -ForegroundColor Green
    Write-Host "The workspace will now automatically clean and optimize itself every week."
} catch {
    Write-Host "❌ Failed to register task. You may need to run this script as Administrator." -ForegroundColor Red
    Write-Host $_.Exception.Message
}

Write-Host "Press any key to exit..."
$Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null

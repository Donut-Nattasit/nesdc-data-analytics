@echo off
title NESDC Data Analysis Setup
echo Starting NESDC Data Analysis Workspace Setup Wizard...
echo.

:: Run the powershell interactive setup script and bypass execution policies
powershell.exe -ExecutionPolicy Bypass -File "%~dp0bin\interactive_setup.ps1"

echo.
pause

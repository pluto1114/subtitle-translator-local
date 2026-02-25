@echo off
setlocal

REM Try to find Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not found in PATH.
    echo Please install Python or add it to your PATH.
    pause
    exit /b 1
)

echo Using Python from:
where python

REM Install required packages
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    echo Please check your internet connection or Python installation.
    pause
    exit /b 1
)

REM Run the application
echo Starting Subtitle Translator...
python main.py

if %errorlevel% neq 0 (
    echo Application crashed or exited with an error.
    pause
)

endlocal

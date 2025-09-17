@echo off
REM Flash Data Logger v0.9 - Windows Installation Script
REM This script installs Flash Data Logger as a standalone package

echo ========================================
echo Flash Data Logger v0.9 - Installation
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Checking Python version compatibility...
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>nul
if errorlevel 1 (
    echo ERROR: Python 3.8+ is required. Found: %PYTHON_VERSION%
    echo Please upgrade Python from https://python.org
    pause
    exit /b 1
)

echo Python version is compatible: %PYTHON_VERSION%
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv flash_data_logger_env
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Virtual environment created successfully
echo.

REM Activate virtual environment
echo Activating virtual environment...
call flash_data_logger_env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing with current version
)

echo.

REM Install the package
echo Installing Flash Data Logger v0.9...
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install Flash Data Logger
    echo This may be due to missing dependencies or network issues
    echo.
    echo Trying to install dependencies manually...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        echo Please check your internet connection and try again
        pause
        exit /b 1
    )
    echo Dependencies installed successfully
    echo Retrying package installation...
    pip install -e .
    if errorlevel 1 (
        echo ERROR: Package installation failed
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.

REM Test installation
echo Testing installation...
python -c "import app.main; print('Flash Data Logger imported successfully')" 2>nul
if errorlevel 1 (
    echo WARNING: Installation test failed, but package may still work
) else (
    echo Installation test passed
)

echo.
echo ========================================
echo Installation Summary
echo ========================================
echo.
echo Flash Data Logger v0.9 has been installed successfully!
echo.
echo To run the application:
echo   1. Open Command Prompt or PowerShell
echo   2. Navigate to this directory
echo   3. Run: flash_data_logger_env\Scripts\activate.bat
echo   4. Run: flash-data-logger
echo.
echo Or use the provided launcher: run_flash_data_logger.bat
echo.
echo IMPORTANT PREREQUISITES:
echo - PicoScope 4262 connected via USB
echo - PicoSDK installed (see PREREQUISITES.md)
echo - Close PicoScope desktop application before running
echo.
echo For troubleshooting, see PREREQUISITES.md
echo.

pause

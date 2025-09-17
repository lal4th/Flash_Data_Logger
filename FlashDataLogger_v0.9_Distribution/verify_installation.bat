@echo off
REM Flash Data Logger v0.9 - Installation Verification
echo ========================================
echo Flash Data Logger v0.9 - Verification
echo ========================================
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
python --version
echo.
echo Checking package installation...
if not exist "flash_data_logger_env\Scripts\activate.bat" (
    echo ERROR: Flash Data Logger is not installed
    echo Please run install_flash_data_logger.bat first
    pause
    exit /b 1
)
echo Package installation found
echo.
echo Testing connectivity...
call flash_data_logger_env\Scripts\activate.bat
python scripts\pico_smoketest.py
echo.
echo Verification complete
pause

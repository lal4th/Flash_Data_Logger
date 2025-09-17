@echo off
REM Flash Data Logger v0.9 - Launcher Script
REM This script launches Flash Data Logger from the installed package

echo ========================================
echo Flash Data Logger v0.9 - Launcher
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "flash_data_logger_env\Scripts\activate.bat" (
    echo ERROR: Flash Data Logger is not installed
    echo Please run install_flash_data_logger.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating Flash Data Logger environment...
call flash_data_logger_env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Environment activated successfully
echo.

REM Check if PicoScope desktop app is running
echo Checking for PicoScope desktop application...
tasklist /FI "IMAGENAME eq PicoScope.exe" 2>NUL | find /I /N "PicoScope.exe" >NUL
if "%ERRORLEVEL%"=="0" (
    echo WARNING: PicoScope desktop application is running
    echo Please close PicoScope before running Flash Data Logger
    echo.
    echo Press any key to continue anyway, or close this window to exit
    pause >nul
)

echo.
echo Starting Flash Data Logger v0.9...
echo.

REM Launch the application
flash-data-logger
if errorlevel 1 (
    echo.
    echo ERROR: Flash Data Logger failed to start
    echo.
    echo Common solutions:
    echo 1. Make sure PicoScope 4262 is connected via USB
    echo 2. Ensure PicoSDK is installed (see PREREQUISITES.md)
    echo 3. Close PicoScope desktop application
    echo 4. Check device drivers are installed
    echo.
    echo For detailed troubleshooting, see PREREQUISITES.md
    echo.
    pause
    exit /b 1
)

echo.
echo Flash Data Logger has closed
pause

@echo off
REM Flash Data Logger v0.9 - Uninstaller
echo ========================================
echo Flash Data Logger v0.9 - Uninstaller
echo ========================================
echo.
echo This will remove Flash Data Logger v0.9 from your system.
echo.
set /p confirm="Are you sure you want to uninstall? (y/N): "
if /i not ""=="y" (
    echo Uninstall cancelled
    pause
    exit /b 0
)
echo.
echo Removing virtual environment...
if exist "flash_data_logger_env" (
    rmdir /s /q "flash_data_logger_env"
    echo Virtual environment removed
) else (
    echo Virtual environment not found
)
echo.
echo Removing cache directory...
if exist "cache" (
    rmdir /s /q "cache"
    echo Cache directory removed
) else (
    echo Cache directory not found
)
echo.
echo Flash Data Logger v0.9 has been uninstalled
echo.
echo Note: This does not remove:
echo - Python installation
echo - PicoSDK installation
echo - Any CSV files you have saved
echo.
pause

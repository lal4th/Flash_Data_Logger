@echo off
echo ========================================
echo INSTALLER DRY RUN TEST
echo ========================================
echo.
echo This is a test version that shows what the installer would do
echo without actually installing anything.
echo.

REM Check for administrator rights (but don't fail)
net session >nul 2>&1
if errorlevel 1 (
    echo WARNING: Administrator rights not detected (this is just a test)
) else (
    echo Administrator rights confirmed.
)
echo.

REM Set installation directory
set "INSTALL_DIR=%PROGRAMFILES%\Flash Data Logger"
echo Would install to: %INSTALL_DIR%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    echo After installing Python, run this installer again.
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Determine source directory - check if we're in the right place
echo Determining source files location...
set "SOURCE_DIR=%CD%"

REM Check if we have the required files in current directory
if exist "app" if exist "requirements.txt" (
    echo ✓ Found source files in current directory: %CD%
    set "SOURCE_DIR=%CD%"
    goto :test_copy
)

REM Check parent directory
if exist "..\app" if exist "..\requirements.txt" (
    echo ✓ Found source files in parent directory: %CD%\..
    set "SOURCE_DIR=%CD%\.."
    goto :test_copy
)

REM If we get here, files are not found
echo ✗ ERROR: Application files not found!
echo.
echo The installer is looking for the 'app' directory and 'requirements.txt' in:
echo - Current directory: %CD%
echo - Parent directory: %CD%\..
echo.
echo Please ensure this installer is run from the correct location:
echo - Either from the root Flash Data Logger directory
echo - Or from the FlashDataLogger_v0.9_Simple directory
echo.
echo Required files: app\ directory and requirements.txt
echo.
pause
exit /b 1

:test_copy
echo ✓ Source directory determined: %SOURCE_DIR%
echo.

echo Would copy application files from: %SOURCE_DIR%
echo.

echo Would copy:
echo - %SOURCE_DIR%\app → %INSTALL_DIR%\app
echo - %SOURCE_DIR%\requirements.txt → %INSTALL_DIR%\requirements.txt
if exist "%SOURCE_DIR%\scripts" echo - %SOURCE_DIR%\scripts → %INSTALL_DIR%\scripts
if exist "%SOURCE_DIR%\setup.py" echo - %SOURCE_DIR%\setup.py → %INSTALL_DIR%\setup.py
if exist "%SOURCE_DIR%\pyproject.toml" echo - %SOURCE_DIR%\pyproject.toml → %INSTALL_DIR%\pyproject.toml
if exist "%SOURCE_DIR%\MANIFEST.in" echo - %SOURCE_DIR%\MANIFEST.in → %INSTALL_DIR%\MANIFEST.in
if exist "%SOURCE_DIR%\LICENSE" echo - %SOURCE_DIR%\LICENSE → %INSTALL_DIR%\LICENSE
if exist "%SOURCE_DIR%\README.md" echo - %SOURCE_DIR%\README.md → %INSTALL_DIR%\README.md
if exist "%SOURCE_DIR%\PREREQUISITES.md" echo - %SOURCE_DIR%\PREREQUISITES.md → %INSTALL_DIR%\PREREQUISITES.md

echo.
echo Would create virtual environment at: %INSTALL_DIR%\venv
echo Would install dependencies from: %INSTALL_DIR%\requirements.txt
echo Would install package from: %INSTALL_DIR%
echo.
echo Would create:
echo - Desktop shortcut: Flash Data Logger
echo - Start menu entry: Flash Data Logger
echo - Uninstaller: %INSTALL_DIR%\uninstall.bat
echo.
echo ========================================
echo DRY RUN COMPLETED SUCCESSFULLY
echo ========================================
echo.
echo The installer logic is working correctly!
echo All required files were found and the installation path was determined.
echo.
pause

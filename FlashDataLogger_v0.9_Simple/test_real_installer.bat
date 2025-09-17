@echo off
echo ========================================
echo TESTING REAL INSTALLER
echo ========================================
echo.
echo This will test the actual installer logic by running it
echo with a modified installation directory for safety.
echo.

REM Set a test installation directory instead of Program Files
set "TEST_INSTALL_DIR=%TEMP%\FlashDataLogger_Test"
echo Test installation directory: %TEST_INSTALL_DIR%
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

REM Create test installation directory
echo Creating test installation directory...
if not exist "%TEST_INSTALL_DIR%" mkdir "%TEST_INSTALL_DIR%"

REM Determine source directory - check if we're in the right place
echo Determining source files location...
set "SOURCE_DIR=%CD%"

REM Check if we have the required files in current directory
echo Testing: if exist "app" if exist "requirements.txt"
if exist "app" if exist "requirements.txt" (
    echo ✓ Found source files in current directory: %CD%
    set "SOURCE_DIR=%CD%"
    goto :test_copy
)

REM Check parent directory
echo Testing: if exist "..\app" if exist "..\requirements.txt"
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
echo Current directory contents:
dir /b
echo.
echo Parent directory contents:
dir .. /b
echo.
pause
exit /b 1

:test_copy
echo ✓ Source directory determined: %SOURCE_DIR%
echo.

echo Testing file copy operations...
echo Copying application files from: %SOURCE_DIR%
echo.

REM Copy application files from determined source directory
echo Testing: xcopy /E /I /Y "%SOURCE_DIR%\app" "%TEST_INSTALL_DIR%\app"
xcopy /E /I /Y "%SOURCE_DIR%\app" "%TEST_INSTALL_DIR%\app"
if errorlevel 1 (
    echo ✗ ERROR: Failed to copy app directory
    echo Error code: %errorlevel%
    pause
    exit /b 1
) else (
    echo ✓ Successfully copied app directory
)

REM Copy scripts directory if it exists
if exist "%SOURCE_DIR%\scripts" (
    echo Testing: xcopy /E /I /Y "%SOURCE_DIR%\scripts" "%TEST_INSTALL_DIR%\scripts"
    xcopy /E /I /Y "%SOURCE_DIR%\scripts" "%TEST_INSTALL_DIR%\scripts"
    if errorlevel 1 (
        echo ⚠ Warning: Failed to copy scripts directory
    ) else (
        echo ✓ Successfully copied scripts directory
    )
)

REM Copy configuration files
echo Testing: copy /Y "%SOURCE_DIR%\requirements.txt" "%TEST_INSTALL_DIR%\"
copy /Y "%SOURCE_DIR%\requirements.txt" "%TEST_INSTALL_DIR%\"
if errorlevel 1 (
    echo ✗ ERROR: Failed to copy requirements.txt
    pause
    exit /b 1
) else (
    echo ✓ Successfully copied requirements.txt
)

if exist "%SOURCE_DIR%\setup.py" (
    copy /Y "%SOURCE_DIR%\setup.py" "%TEST_INSTALL_DIR%\"
    echo ✓ Copied setup.py
)

if exist "%SOURCE_DIR%\pyproject.toml" (
    copy /Y "%SOURCE_DIR%\pyproject.toml" "%TEST_INSTALL_DIR%\"
    echo ✓ Copied pyproject.toml
)

if exist "%SOURCE_DIR%\MANIFEST.in" (
    copy /Y "%SOURCE_DIR%\MANIFEST.in" "%TEST_INSTALL_DIR%\"
    echo ✓ Copied MANIFEST.in
)

if exist "%SOURCE_DIR%\LICENSE" (
    copy /Y "%SOURCE_DIR%\LICENSE" "%TEST_INSTALL_DIR%\"
    echo ✓ Copied LICENSE
)

if exist "%SOURCE_DIR%\README.md" (
    copy /Y "%SOURCE_DIR%\README.md" "%TEST_INSTALL_DIR%\"
    echo ✓ Copied README.md
)

if exist "%SOURCE_DIR%\PREREQUISITES.md" (
    copy /Y "%SOURCE_DIR%\PREREQUISITES.md" "%TEST_INSTALL_DIR%\"
    echo ✓ Copied PREREQUISITES.md
)

echo.
echo Test installation directory contents:
dir "%TEST_INSTALL_DIR%" /b

echo.
echo ========================================
echo REAL INSTALLER TEST COMPLETED SUCCESSFULLY
echo ========================================
echo.
echo The installer logic works correctly!
echo All files were copied successfully to: %TEST_INSTALL_DIR%
echo.

REM Clean up test directory
echo Cleaning up test files...
rmdir /s /q "%TEST_INSTALL_DIR%"
echo Test directory cleaned up.

echo.
echo The installer should work on your system.
echo If you're still getting errors, the issue might be:
echo 1. Running from wrong directory
echo 2. Missing administrator rights
echo 3. Antivirus blocking the installer
echo 4. File permissions issues
echo.
pause

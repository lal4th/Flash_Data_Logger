@echo off
echo ========================================
echo INSTALLER DEBUG TEST
echo ========================================
echo.
echo Current directory: %CD%
echo.
echo Checking for required files:
echo.

echo 1. Checking for 'app' directory:
if exist "app" (
    echo    ✓ app directory found in current directory
    dir app /b | findstr /v "^$" | findstr /c:"__init__.py" >nul
    if errorlevel 1 (
        echo    ⚠ app directory exists but may be empty or missing __init__.py
    ) else (
        echo    ✓ app directory contains Python files
    )
) else (
    echo    ✗ app directory NOT found in current directory
)

echo.
echo 2. Checking for 'requirements.txt':
if exist "requirements.txt" (
    echo    ✓ requirements.txt found in current directory
    for /f %%i in ('type requirements.txt ^| find /c /v ""') do set lines=%%i
    echo    ✓ requirements.txt has %lines% lines
) else (
    echo    ✗ requirements.txt NOT found in current directory
)

echo.
echo 3. Checking parent directory:
echo    Parent directory: %CD%\..
if exist "..\app" (
    echo    ✓ app directory found in parent directory
) else (
    echo    ✗ app directory NOT found in parent directory
)

if exist "..\requirements.txt" (
    echo    ✓ requirements.txt found in parent directory
) else (
    echo    ✗ requirements.txt NOT found in parent directory
)

echo.
echo 4. Testing installer logic:
echo    Testing: if exist "app" if exist "requirements.txt"
if exist "app" if exist "requirements.txt" (
    echo    ✓ Both files found in current directory - installer should work
    set "TEST_RESULT=CURRENT_DIR"
) else (
    echo    ✗ Files not found in current directory
    echo    Testing: if exist "..\app" if exist "..\requirements.txt"
    if exist "..\app" if exist "..\requirements.txt" (
        echo    ✓ Both files found in parent directory - installer should work
        set "TEST_RESULT=PARENT_DIR"
    ) else (
        echo    ✗ Files not found in parent directory either
        set "TEST_RESULT=FAIL"
    )
)

echo.
echo 5. Directory listing:
echo    Current directory contents:
dir /b 2>nul | findstr /v "^$"

echo.
echo 6. Test result: %TEST_RESULT%
echo.
pause

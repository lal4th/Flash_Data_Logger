@echo off
echo ========================================
echo SIMPLE TEST - This should stay open
echo ========================================
echo.
echo Current directory: %CD%
echo.
echo Checking for app directory:
if exist "app" (
    echo FOUND: app directory exists
) else (
    echo NOT FOUND: app directory does not exist
)
echo.
echo Checking for requirements.txt:
if exist "requirements.txt" (
    echo FOUND: requirements.txt exists
) else (
    echo NOT FOUND: requirements.txt does not exist
)
echo.
echo Directory contents:
dir /b
echo.
echo Press any key to exit...
pause

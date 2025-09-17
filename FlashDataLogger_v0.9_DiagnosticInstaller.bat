@echo off
REM Flash Data Logger v0.9 - Diagnostic Installer
REM This version provides detailed diagnostic information

title Flash Data Logger v0.9 - Diagnostic Installer

echo ========================================
echo Flash Data Logger v0.9 - Diagnostic Installer
echo ========================================
echo.
echo This installer provides detailed diagnostic information
echo to help troubleshoot installation issues.
echo.

REM Check for administrator rights
echo [DIAGNOSTIC] Checking for administrator rights...
net session >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Administrator rights required!
    echo.
    echo Please right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
) else (
    echo [OK] Administrator rights confirmed.
)
echo.

REM Set installation directory
set "INSTALL_DIR=%PROGRAMFILES%\Flash Data Logger"
echo [DIAGNOSTIC] Installation directory: %INSTALL_DIR%
echo.

REM Check if Python is installed
echo [DIAGNOSTIC] Checking for Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    echo After installing Python, run this installer again.
    pause
    exit /b 1
) else (
    echo [OK] Python found:
    python --version
)
echo.

REM Create installation directory
echo [DIAGNOSTIC] Creating installation directory...
if not exist "%INSTALL_DIR%" (
    echo [INFO] Creating directory: %INSTALL_DIR%
    mkdir "%INSTALL_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to create installation directory
        echo This may be due to insufficient permissions.
        pause
        exit /b 1
    ) else (
        echo [OK] Installation directory created successfully
    )
) else (
    echo [INFO] Installation directory already exists
)
echo.

REM Detailed diagnostic information
echo [DIAGNOSTIC] Current working directory: %CD%
echo [DIAGNOSTIC] Current directory contents:
dir /b
echo.

echo [DIAGNOSTIC] Parent directory: %CD%\..
echo [DIAGNOSTIC] Parent directory contents:
dir .. /b
echo.

REM Determine source directory - check if we're in the right place
echo [DIAGNOSTIC] Determining source files location...
set "SOURCE_DIR=%CD%"

REM Check if we have the required files in current directory
echo [DIAGNOSTIC] Testing current directory for required files...
echo [DIAGNOSTIC] Checking: if exist "app"
if exist "app" (
    echo [OK] app directory found in current directory
    echo [DIAGNOSTIC] app directory contents:
    dir app /b
) else (
    echo [FAIL] app directory NOT found in current directory
)

echo [DIAGNOSTIC] Checking: if exist "requirements.txt"
if exist "requirements.txt" (
    echo [OK] requirements.txt found in current directory
    echo [DIAGNOSTIC] requirements.txt contents (first 5 lines):
    more +1 requirements.txt | findstr /n "^" | findstr "^[1-5]:"
) else (
    echo [FAIL] requirements.txt NOT found in current directory
)

echo.
echo [DIAGNOSTIC] Testing combined condition: if exist "app" if exist "requirements.txt"
if exist "app" if exist "requirements.txt" (
    echo [OK] Both required files found in current directory: %CD%
    set "SOURCE_DIR=%CD%"
    goto :copy_files
) else (
    echo [FAIL] Required files not found in current directory
)

REM Check parent directory
echo [DIAGNOSTIC] Testing parent directory for required files...
echo [DIAGNOSTIC] Checking: if exist "..\app"
if exist "..\app" (
    echo [OK] app directory found in parent directory
    echo [DIAGNOSTIC] parent app directory contents:
    dir ..\app /b
) else (
    echo [FAIL] app directory NOT found in parent directory
)

echo [DIAGNOSTIC] Checking: if exist "..\requirements.txt"
if exist "..\requirements.txt" (
    echo [OK] requirements.txt found in parent directory
    echo [DIAGNOSTIC] parent requirements.txt contents (first 5 lines):
    more +1 ..\requirements.txt | findstr /n "^" | findstr "^[1-5]:"
) else (
    echo [FAIL] requirements.txt NOT found in parent directory
)

echo.
echo [DIAGNOSTIC] Testing combined condition: if exist "..\app" if exist "..\requirements.txt"
if exist "..\app" if exist "..\requirements.txt" (
    echo [OK] Both required files found in parent directory: %CD%\..
    set "SOURCE_DIR=%CD%\.."
    goto :copy_files
) else (
    echo [FAIL] Required files not found in parent directory
)

REM If we get here, files are not found
echo [ERROR] Application files not found!
echo.
echo [DIAGNOSTIC] The installer is looking for the 'app' directory and 'requirements.txt' in:
echo - Current directory: %CD%
echo - Parent directory: %CD%\..
echo.
echo [DIAGNOSTIC] Please ensure this installer is run from the correct location:
echo - Either from the root Flash Data Logger directory
echo - Or from the FlashDataLogger_v0.9_Simple directory
echo.
echo [DIAGNOSTIC] Required files: app\ directory and requirements.txt
echo.
echo [DIAGNOSTIC] Full directory listing for current directory:
dir /a
echo.
echo [DIAGNOSTIC] Full directory listing for parent directory:
dir .. /a
echo.
pause
exit /b 1

:copy_files
echo [OK] Source directory determined: %SOURCE_DIR%
echo.

echo [DIAGNOSTIC] Copying application files from: %SOURCE_DIR%
echo.

REM Copy application files from determined source directory
echo [DIAGNOSTIC] Copying app directory...
xcopy /E /I /Y "%SOURCE_DIR%\app" "%INSTALL_DIR%\app"
if errorlevel 1 (
    echo [ERROR] Failed to copy app directory
    echo [DIAGNOSTIC] Error code: %errorlevel%
    echo [DIAGNOSTIC] Source: %SOURCE_DIR%\app
    echo [DIAGNOSTIC] Destination: %INSTALL_DIR%\app
    pause
    exit /b 1
) else (
    echo [OK] Successfully copied app directory
)

REM Copy scripts directory if it exists
if exist "%SOURCE_DIR%\scripts" (
    echo [DIAGNOSTIC] Copying scripts directory...
    xcopy /E /I /Y "%SOURCE_DIR%\scripts" "%INSTALL_DIR%\scripts"
    if errorlevel 1 (
        echo [WARNING] Failed to copy scripts directory
    ) else (
        echo [OK] Successfully copied scripts directory
    )
)

REM Copy configuration files
echo [DIAGNOSTIC] Copying configuration files...
if exist "%SOURCE_DIR%\requirements.txt" (
    copy /Y "%SOURCE_DIR%\requirements.txt" "%INSTALL_DIR%\"
    if errorlevel 1 (
        echo [ERROR] Failed to copy requirements.txt
        pause
        exit /b 1
    ) else (
        echo [OK] Copied requirements.txt
    )
)

if exist "%SOURCE_DIR%\setup.py" (
    copy /Y "%SOURCE_DIR%\setup.py" "%INSTALL_DIR%\"
    echo [OK] Copied setup.py
)

if exist "%SOURCE_DIR%\pyproject.toml" (
    copy /Y "%SOURCE_DIR%\pyproject.toml" "%INSTALL_DIR%\"
    echo [OK] Copied pyproject.toml
)

if exist "%SOURCE_DIR%\MANIFEST.in" (
    copy /Y "%SOURCE_DIR%\MANIFEST.in" "%INSTALL_DIR%\"
    echo [OK] Copied MANIFEST.in
)

if exist "%SOURCE_DIR%\LICENSE" (
    copy /Y "%SOURCE_DIR%\LICENSE" "%INSTALL_DIR%\"
    echo [OK] Copied LICENSE
)

if exist "%SOURCE_DIR%\README.md" (
    copy /Y "%SOURCE_DIR%\README.md" "%INSTALL_DIR%\"
    echo [OK] Copied README.md
)

if exist "%SOURCE_DIR%\PREREQUISITES.md" (
    copy /Y "%SOURCE_DIR%\PREREQUISITES.md" "%INSTALL_DIR%\"
    echo [OK] Copied PREREQUISITES.md
)

echo [OK] Application files copied successfully.
echo.

REM Create virtual environment
echo [DIAGNOSTIC] Creating Python virtual environment...
python -m venv "%INSTALL_DIR%\venv"
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    echo [DIAGNOSTIC] This may be due to insufficient permissions or Python issues.
    pause
    exit /b 1
) else (
    echo [OK] Virtual environment created successfully.
)
echo.

REM Install dependencies
echo [DIAGNOSTIC] Installing Python dependencies...
echo [INFO] This may take a few minutes...
call "%INSTALL_DIR%\venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
) else (
    echo [OK] Virtual environment activated successfully
)

echo [DIAGNOSTIC] Upgrading pip...
pip install --upgrade pip
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing with current version
) else (
    echo [OK] Pip upgraded successfully
)

echo [DIAGNOSTIC] Installing dependencies from requirements.txt...
pip install -r "%INSTALL_DIR%\requirements.txt"
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo [DIAGNOSTIC] This may be due to network issues or missing packages.
    pause
    exit /b 1
) else (
    echo [OK] Dependencies installed successfully
)

echo [DIAGNOSTIC] Installing Flash Data Logger package...
pip install "%INSTALL_DIR%"
if errorlevel 1 (
    echo [WARNING] Package installation failed, but dependencies are installed
    echo [INFO] The application may still work.
) else (
    echo [OK] Package installed successfully
)

echo [OK] Dependencies installed successfully.
echo.

REM Create launcher script
echo [DIAGNOSTIC] Creating launcher script...
(
echo @echo off
echo title Flash Data Logger v0.9
echo cd /d "%INSTALL_DIR%"
echo call venv\Scripts\activate.bat
echo python -m app.main
echo if errorlevel 1 (
echo     echo.
echo     echo Application encountered an error.
echo     echo Please check that PicoScope 4262 is connected and PicoSDK is installed.
echo     echo See PREREQUISITES.md for troubleshooting.
echo     echo.
echo     pause
echo ^)
) > "%INSTALL_DIR%\FlashDataLogger.bat"

echo [OK] Launcher script created.
echo.

REM Create desktop shortcut
echo [DIAGNOSTIC] Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Flash Data Logger.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\FlashDataLogger.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Flash Data Logger v0.9 - PicoScope Data Acquisition'; $Shortcut.Save()" 2>nul
if errorlevel 1 (
    echo [WARNING] Failed to create desktop shortcut
) else (
    echo [OK] Desktop shortcut created successfully.
)

REM Create start menu shortcut
echo [DIAGNOSTIC] Creating start menu entry...
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Flash Data Logger" mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Flash Data Logger"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Flash Data Logger\Flash Data Logger.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\FlashDataLogger.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Flash Data Logger v0.9 - PicoScope Data Acquisition'; $Shortcut.Save()" 2>nul
if errorlevel 1 (
    echo [WARNING] Failed to create start menu shortcut
) else (
    echo [OK] Start menu entry created successfully.
)

REM Create uninstaller
echo [DIAGNOSTIC] Creating uninstaller...
(
echo @echo off
echo title Flash Data Logger v0.9 - Uninstaller
echo echo ========================================
echo echo Flash Data Logger v0.9 - Uninstaller
echo echo ========================================
echo echo.
echo echo This will remove Flash Data Logger v0.9 from your system.
echo echo.
echo set /p confirm="Are you sure you want to uninstall? (y/N): "
echo if /i not "%%confirm%%"=="y" (
echo     echo Uninstall cancelled
echo     pause
echo     exit /b 0
echo ^)
echo echo.
echo echo Removing application files...
echo rmdir /s /q "%INSTALL_DIR%"
echo echo.
echo echo Removing shortcuts...
echo del "%USERPROFILE%\Desktop\Flash Data Logger.lnk" 2^>nul
echo rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Flash Data Logger" 2^>nul
echo echo.
echo echo Flash Data Logger v0.9 has been uninstalled successfully.
echo echo.
echo pause
) > "%INSTALL_DIR%\uninstall.bat"

echo [OK] Uninstaller created.
echo.

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo [OK] Flash Data Logger v0.9 has been installed successfully!
echo.
echo [INFO] Installation location: %INSTALL_DIR%
echo [INFO] Desktop shortcut: Flash Data Logger
echo [INFO] Start menu: Flash Data Logger
echo.
echo [INFO] IMPORTANT NEXT STEPS:
echo 1. Install PicoSDK from Pico Technology website
echo 2. Connect PicoScope 4262 via USB
echo 3. Close PicoScope desktop application
echo 4. Double-click desktop shortcut to launch
echo.
echo [INFO] For troubleshooting, see PREREQUISITES.md in the installation directory.
echo [INFO] To uninstall: Run uninstall.bat in the installation directory
echo.

REM Ask if user wants to launch the application
set /p launch="Would you like to launch Flash Data Logger now? (y/N): "
if /i "%launch%"=="y" (
    echo.
    echo [INFO] Launching Flash Data Logger...
    start "" "%INSTALL_DIR%\FlashDataLogger.bat"
)

echo.
echo [OK] Thank you for installing Flash Data Logger v0.9!
pause

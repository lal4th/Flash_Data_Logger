@echo off
REM Flash Data Logger v0.9 - Simple One-Click Installer
REM This is a single file that installs everything automatically

title Flash Data Logger v0.9 - Simple Installer

echo ========================================
echo Flash Data Logger v0.9 - Simple Installer
echo ========================================
echo.
echo This installer will automatically:
echo - Install Flash Data Logger to Program Files
echo - Create desktop shortcut
echo - Create start menu entry
echo - Handle Python dependencies
echo.
echo IMPORTANT: You must run this as Administrator
echo.

REM Check for administrator rights
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: Administrator rights required!
    echo.
    echo Please right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Administrator rights confirmed.
echo.

REM Set installation directory
set "INSTALL_DIR=%PROGRAMFILES%\Flash Data Logger"
echo Installing to: %INSTALL_DIR%
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

REM Create installation directory
echo Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy application files (check current directory and parent directory)
echo Copying application files...
if exist "app" (
    echo Found app directory in current location
    xcopy /E /I /Y "app" "%INSTALL_DIR%\app"
) else if exist "..\app" (
    echo Found app directory in parent location
    xcopy /E /I /Y "..\app" "%INSTALL_DIR%\app"
) else (
    echo ERROR: Application files not found!
    echo.
    echo The installer is looking for the 'app' directory in:
    echo - Current directory: %CD%
    echo - Parent directory: %CD%\..
    echo.
    echo Please ensure this installer is run from the correct location:
    echo - Either from the root Flash Data Logger directory
    echo - Or from the FlashDataLogger_v0.9_Simple directory
    echo.
    pause
    exit /b 1
)

REM Copy other files (check both current and parent directory)
if exist "scripts" (
    xcopy /E /I /Y "scripts" "%INSTALL_DIR%\scripts"
) else if exist "..\scripts" (
    xcopy /E /I /Y "..\scripts" "%INSTALL_DIR%\scripts"
)

if exist "requirements.txt" (
    copy /Y "requirements.txt" "%INSTALL_DIR%\"
) else if exist "..\requirements.txt" (
    copy /Y "..\requirements.txt" "%INSTALL_DIR%\"
)

if exist "setup.py" (
    copy /Y "setup.py" "%INSTALL_DIR%\"
) else if exist "..\setup.py" (
    copy /Y "..\setup.py" "%INSTALL_DIR%\"
)

if exist "pyproject.toml" (
    copy /Y "pyproject.toml" "%INSTALL_DIR%\"
) else if exist "..\pyproject.toml" (
    copy /Y "..\pyproject.toml" "%INSTALL_DIR%\"
)

if exist "MANIFEST.in" (
    copy /Y "MANIFEST.in" "%INSTALL_DIR%\"
) else if exist "..\MANIFEST.in" (
    copy /Y "..\MANIFEST.in" "%INSTALL_DIR%\"
)

if exist "LICENSE" (
    copy /Y "LICENSE" "%INSTALL_DIR%\"
) else if exist "..\LICENSE" (
    copy /Y "..\LICENSE" "%INSTALL_DIR%\"
)

if exist "README.md" (
    copy /Y "README.md" "%INSTALL_DIR%\"
) else if exist "..\README.md" (
    copy /Y "..\README.md" "%INSTALL_DIR%\"
)

if exist "PREREQUISITES.md" (
    copy /Y "PREREQUISITES.md" "%INSTALL_DIR%\"
) else if exist "..\PREREQUISITES.md" (
    copy /Y "..\PREREQUISITES.md" "%INSTALL_DIR%\"
)

echo Application files copied successfully.
echo.

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv "%INSTALL_DIR%\venv"
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo This may be due to insufficient permissions or Python issues.
    pause
    exit /b 1
)

echo Virtual environment created successfully.
echo.

REM Install dependencies
echo Installing Python dependencies...
echo This may take a few minutes...
call "%INSTALL_DIR%\venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Upgrading pip...
pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing with current version
)

echo Installing dependencies from requirements.txt...
pip install -r "%INSTALL_DIR%\requirements.txt"
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo This may be due to network issues or missing packages.
    pause
    exit /b 1
)

echo Installing Flash Data Logger package...
pip install "%INSTALL_DIR%"
if errorlevel 1 (
    echo WARNING: Package installation failed, but dependencies are installed
    echo The application may still work.
)

echo Dependencies installed successfully.
echo.

REM Create launcher script
echo Creating launcher script...
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

echo Launcher script created.
echo.

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Flash Data Logger.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\FlashDataLogger.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Flash Data Logger v0.9 - PicoScope Data Acquisition'; $Shortcut.Save()" 2>nul
if errorlevel 1 (
    echo WARNING: Failed to create desktop shortcut
) else (
    echo Desktop shortcut created successfully.
)

REM Create start menu shortcut
echo Creating start menu entry...
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Flash Data Logger" mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Flash Data Logger"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Flash Data Logger\Flash Data Logger.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\FlashDataLogger.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Flash Data Logger v0.9 - PicoScope Data Acquisition'; $Shortcut.Save()" 2>nul
if errorlevel 1 (
    echo WARNING: Failed to create start menu shortcut
) else (
    echo Start menu entry created successfully.
)

REM Create uninstaller
echo Creating uninstaller...
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

echo Uninstaller created.
echo.

REM Create a simple README for the installation
(
echo Flash Data Logger v0.9 - Installation Complete
echo ==============================================
echo.
echo Installation Location: %INSTALL_DIR%
echo.
echo To launch Flash Data Logger:
echo - Double-click the desktop shortcut "Flash Data Logger"
echo - Or find it in the Start Menu under "Flash Data Logger"
echo.
echo Prerequisites:
echo - PicoScope 4262 connected via USB
echo - PicoSDK installed (download from Pico Technology website)
echo - Close PicoScope desktop application before running
echo.
echo Troubleshooting:
echo - See PREREQUISITES.md for detailed setup instructions
echo - Run the connectivity test: python scripts\pico_smoketest.py
echo.
echo To uninstall:
echo - Run uninstall.bat in the installation directory
echo.
) > "%INSTALL_DIR%\INSTALLATION_COMPLETE.txt"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Flash Data Logger v0.9 has been installed successfully!
echo.
echo Installation location: %INSTALL_DIR%
echo.
echo Desktop shortcut: Flash Data Logger
echo Start menu: Flash Data Logger
echo.
echo IMPORTANT NEXT STEPS:
echo 1. Install PicoSDK from Pico Technology website
echo 2. Connect PicoScope 4262 via USB
echo 3. Close PicoScope desktop application
echo 4. Double-click desktop shortcut to launch
echo.
echo For troubleshooting, see PREREQUISITES.md in the installation directory.
echo.
echo To uninstall: Run uninstall.bat in the installation directory
echo.

REM Ask if user wants to launch the application
set /p launch="Would you like to launch Flash Data Logger now? (y/N): "
if /i "%launch%"=="y" (
    echo.
    echo Launching Flash Data Logger...
    start "" "%INSTALL_DIR%\FlashDataLogger.bat"
)

echo.
echo Thank you for installing Flash Data Logger v0.9!
pause

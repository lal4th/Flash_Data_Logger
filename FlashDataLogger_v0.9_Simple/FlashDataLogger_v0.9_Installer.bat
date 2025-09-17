@echo off
REM Flash Data Logger v0.9 - Fixed Installer
REM This version automatically changes to the correct directory

title Flash Data Logger v0.9 - Fixed Installer

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo ========================================
echo Flash Data Logger v0.9 - Fixed Installer
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

REM Determine source directory - check if we're in the right place
echo Determining source files location...
set "SOURCE_DIR=%CD%"

REM Check if we have the required files in current directory
if exist "app" if exist "requirements.txt" (
    echo Found source files in current directory: %CD%
    set "SOURCE_DIR=%CD%"
    goto :copy_files
)

REM Check parent directory
if exist "..\app" if exist "..\requirements.txt" (
    echo Found source files in parent directory: %CD%\..
    set "SOURCE_DIR=%CD%\.."
    goto :copy_files
)

REM If we get here, files are not found
echo ERROR: Application files not found!
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

:copy_files
echo Copying application files from: %SOURCE_DIR%
echo.

REM Copy application files from determined source directory
xcopy /E /I /Y "%SOURCE_DIR%\app" "%INSTALL_DIR%\app"
if errorlevel 1 (
    echo ERROR: Failed to copy app directory
    pause
    exit /b 1
)

REM Copy scripts directory if it exists
if exist "%SOURCE_DIR%\scripts" (
    xcopy /E /I /Y "%SOURCE_DIR%\scripts" "%INSTALL_DIR%\scripts"
)

REM Copy configuration files
if exist "%SOURCE_DIR%\requirements.txt" copy /Y "%SOURCE_DIR%\requirements.txt" "%INSTALL_DIR%\"
if exist "%SOURCE_DIR%\setup.py" copy /Y "%SOURCE_DIR%\setup.py" "%INSTALL_DIR%\"
if exist "%SOURCE_DIR%\pyproject.toml" copy /Y "%SOURCE_DIR%\pyproject.toml" "%INSTALL_DIR%\"
if exist "%SOURCE_DIR%\MANIFEST.in" copy /Y "%SOURCE_DIR%\MANIFEST.in" "%INSTALL_DIR%\"
if exist "%SOURCE_DIR%\LICENSE" copy /Y "%SOURCE_DIR%\LICENSE" "%INSTALL_DIR%\"
if exist "%SOURCE_DIR%\README.md" copy /Y "%SOURCE_DIR%\README.md" "%INSTALL_DIR%\"
if exist "%SOURCE_DIR%\PREREQUISITES.md" copy /Y "%SOURCE_DIR%\PREREQUISITES.md" "%INSTALL_DIR%\"

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

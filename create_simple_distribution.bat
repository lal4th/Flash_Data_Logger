@echo off
REM Flash Data Logger v0.9 - Simple Distribution Creator
REM Creates a simple distribution with the one-click installer

echo ========================================
echo Flash Data Logger v0.9 - Simple Distribution
echo ========================================
echo.

set DIST_DIR=FlashDataLogger_v0.9_Simple
set PACKAGE_NAME=FlashDataLogger_v0.9_Simple

echo Creating simple distribution package: %PACKAGE_NAME%
echo.

REM Clean previous distribution
if exist "%DIST_DIR%" (
    echo Cleaning previous distribution...
    rmdir /s /q "%DIST_DIR%"
)

REM Create distribution directory
mkdir "%DIST_DIR%"
cd "%DIST_DIR%"

echo Copying application files...

REM Copy core application files
xcopy /E /I /Y "..\app" "app"
xcopy /E /I /Y "..\scripts" "scripts"

REM Copy configuration files
copy "..\requirements.txt" "requirements.txt"
copy "..\setup.py" "setup.py"
copy "..\pyproject.toml" "pyproject.toml"
copy "..\MANIFEST.in" "MANIFEST.in"
copy "..\LICENSE" "LICENSE"

REM Copy documentation
copy "..\README.md" "README.md"
copy "..\PREREQUISITES.md" "PREREQUISITES.md"
copy "..\INSTALLATION_GUIDE.md" "INSTALLATION_GUIDE.md"
copy "..\SIMPLE_INSTALLER_GUIDE.md" "SIMPLE_INSTALLER_GUIDE.md"

REM Copy the simple installer
copy "..\FlashDataLogger_v0.9_SimpleInstaller.bat" "FlashDataLogger_v0.9_SimpleInstaller.bat"

REM Create a simple README for the distribution
(
echo # Flash Data Logger v0.9 - Simple Distribution
echo.
echo This package contains Flash Data Logger v0.9 with a simple one-click installer.
echo.
echo ## Quick Installation
echo.
echo 1. **Right-click** `FlashDataLogger_v0.9_SimpleInstaller.bat`
echo 2. **Select** "Run as administrator"
echo 3. **Follow** the installation prompts
echo 4. **Double-click** the desktop shortcut to launch
echo.
echo ## What the Installer Does
echo.
echo - Installs Flash Data Logger to Program Files
echo - Creates desktop shortcut
echo - Creates start menu entry
echo - Handles Python dependencies automatically
echo - Creates uninstaller
echo.
echo ## Prerequisites
echo.
echo - Windows 10/11 ^(64-bit^)
echo - Python 3.8+ installed with PATH
echo - PicoScope 4262 connected via USB
echo - PicoSDK installed separately
echo.
echo ## After Installation
echo.
echo 1. Install PicoSDK from Pico Technology website
echo 2. Connect PicoScope 4262 via USB
echo 3. Close PicoScope desktop application
echo 4. Double-click desktop shortcut to launch
echo.
echo ## Support
echo.
echo - See PREREQUISITES.md for detailed setup
echo - See SIMPLE_INSTALLER_GUIDE.md for installer details
echo - GitHub Issues for support
echo.
echo ---
echo **Flash Data Logger v0.9** - Simple one-click installation
) > "SIMPLE_DISTRIBUTION_README.md"

echo.
echo Creating version information...

REM Create version file
(
echo Flash Data Logger v0.9 - Simple Distribution
echo Build Date: %DATE% %TIME%
echo.
echo Package Contents:
echo - One-click installer (FlashDataLogger_v0.9_SimpleInstaller.bat)
echo - Complete application code
echo - All dependencies and documentation
echo.
echo Installation: Right-click installer and "Run as administrator"
echo Launch: Double-click desktop shortcut after installation
echo.
echo Features:
echo - Math Channel Functionality
echo - Multi-Channel Acquisition
echo - Real-time Data Streaming
echo - Dynamic Plot Management
echo - CSV Export with Math Channels
echo - Synchronized Scrolling
echo - Mirror Windows
) > "VERSION.txt"

echo.
echo Simple distribution package created successfully!
echo.
echo ========================================
echo Distribution Summary
echo ========================================
echo.
echo Package: %DIST_DIR%
echo Location: %CD%
echo.
echo Contents:
echo - Complete Flash Data Logger v0.9 application
echo - Simple one-click installer
echo - Comprehensive documentation
echo.
echo To distribute:
echo 1. Zip the %DIST_DIR% folder
echo 2. Share the zip file with users
echo 3. Users extract and run FlashDataLogger_v0.9_SimpleInstaller.bat as Administrator
echo.
echo Installation instructions:
echo - Users right-click installer and "Run as administrator"
echo - No command line knowledge required
echo - Automatic Python dependency handling
echo - Professional installation to Program Files
echo.

cd ..

echo Simple distribution package ready: %DIST_DIR%
echo.
pause

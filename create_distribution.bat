@echo off
REM Flash Data Logger v0.9 - Distribution Package Creator
REM This script creates a complete distribution package for Windows

echo ========================================
echo Flash Data Logger v0.9 - Distribution
echo ========================================
echo.

REM Set distribution directory
set DIST_DIR=FlashDataLogger_v0.9_Distribution
set PACKAGE_NAME=FlashDataLogger_v0.9

echo Creating distribution package: %PACKAGE_NAME%
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

REM Copy documentation
copy "..\README.md" "README.md"
copy "..\REQUIREMENTS.md" "REQUIREMENTS.md"
copy "..\PREREQUISITES.md" "PREREQUISITES.md"
copy "..\INSTALLATION_GUIDE.md" "INSTALLATION_GUIDE.md"
copy "..\Handoff_to_v1.0.md" "Handoff_to_v1.0.md"

REM Copy configuration files
copy "..\requirements.txt" "requirements.txt"
copy "..\setup.py" "setup.py"
copy "..\pyproject.toml" "pyproject.toml"
copy "..\MANIFEST.in" "MANIFEST.in"
copy "..\LICENSE" "LICENSE"

REM Copy installation scripts
copy "..\install_flash_data_logger.bat" "install_flash_data_logger.bat"
copy "..\run_flash_data_logger.bat" "run_flash_data_logger.bat"

REM Copy PDF documentation if available
if exist "..\picoscope-4000-series-programmers-guide.pdf" (
    copy "..\picoscope-4000-series-programmers-guide.pdf" "picoscope-4000-series-programmers-guide.pdf"
)
if exist "..\picoscope-4000-series-user-guide.pdf" (
    copy "..\picoscope-4000-series-user-guide.pdf" "picoscope-4000-series-user-guide.pdf"
)
if exist "..\picoscope-4262-data-sheet.pdf" (
    copy "..\picoscope-4262-data-sheet.pdf" "picoscope-4262-data-sheet.pdf"
)

REM Create cache directory
mkdir "cache"

echo.
echo Creating distribution README...

REM Create distribution-specific README
(
echo # Flash Data Logger v0.9 - Distribution Package
echo.
echo This package contains the complete Flash Data Logger v0.9 application
echo for Windows 10/11 with PicoScope 4262 support.
echo.
echo ## Quick Start
echo.
echo 1. **Read PREREQUISITES.md** - Complete setup requirements
echo 2. **Run install_flash_data_logger.bat** - Automated installation
echo 3. **Run run_flash_data_logger.bat** - Launch application
echo.
echo ## Package Contents
echo.
echo - **app/** - Main application code
echo - **scripts/** - Utility scripts and tests
echo - **install_flash_data_logger.bat** - Automated installer
echo - **run_flash_data_logger.bat** - Application launcher
echo - **PREREQUISITES.md** - Detailed prerequisites guide
echo - **INSTALLATION_GUIDE.md** - Step-by-step installation
echo - **README.md** - Main documentation
echo.
echo ## Requirements
echo.
echo - Windows 10/11 ^(64-bit^)
echo - Python 3.8+
echo - PicoScope 4262 connected via USB
echo - PicoSDK installed
echo.
echo ## Installation
echo.
echo 1. Ensure all prerequisites are met ^(see PREREQUISITES.md^)
echo 2. Double-click **install_flash_data_logger.bat**
echo 3. Follow the installation prompts
echo 4. Run **run_flash_data_logger.bat** to launch
echo.
echo ## Support
echo.
echo - **Prerequisites**: PREREQUISITES.md
echo - **Installation**: INSTALLATION_GUIDE.md
echo - **Documentation**: README.md
echo - **Issues**: GitHub Issues
echo.
echo ---
echo **Flash Data Logger v0.9** - Production-ready PicoScope data acquisition
) > "DISTRIBUTION_README.md"

echo.
echo Creating version information...

REM Create version file
(
echo Flash Data Logger v0.9
echo Build Date: %DATE% %TIME%
echo Python Version: 
python --version 2>nul || echo Python not found in PATH
echo.
echo Package Contents:
echo - Math Channel Functionality
echo - Multi-Channel Acquisition
echo - Real-time Data Streaming
echo - Dynamic Plot Management
echo - CSV Export with Math Channels
echo - Synchronized Scrolling
echo - Mirror Windows
echo.
echo Installation: Run install_flash_data_logger.bat
echo Launch: Run run_flash_data_logger.bat
) > "VERSION.txt"

echo.
echo Creating installation verification script...

REM Create verification script
(
echo @echo off
echo REM Flash Data Logger v0.9 - Installation Verification
echo echo ========================================
echo echo Flash Data Logger v0.9 - Verification
echo echo ========================================
echo echo.
echo echo Checking Python installation...
echo python --version ^>nul 2^>^&1
echo if errorlevel 1 ^(
echo     echo ERROR: Python is not installed or not in PATH
echo     echo Please install Python 3.8+ from https://python.org
echo     pause
echo     exit /b 1
echo ^)
echo python --version
echo echo.
echo echo Checking package installation...
echo if not exist "flash_data_logger_env\Scripts\activate.bat" ^(
echo     echo ERROR: Flash Data Logger is not installed
echo     echo Please run install_flash_data_logger.bat first
echo     pause
echo     exit /b 1
echo ^)
echo echo Package installation found
echo echo.
echo echo Testing connectivity...
echo call flash_data_logger_env\Scripts\activate.bat
echo python scripts\pico_smoketest.py
echo echo.
echo echo Verification complete
echo pause
) > "verify_installation.bat"

echo.
echo Creating uninstaller script...

REM Create uninstaller
(
echo @echo off
echo REM Flash Data Logger v0.9 - Uninstaller
echo echo ========================================
echo echo Flash Data Logger v0.9 - Uninstaller
echo echo ========================================
echo echo.
echo echo This will remove Flash Data Logger v0.9 from your system.
echo echo.
echo set /p confirm="Are you sure you want to uninstall? (y/N): "
echo if /i not "%confirm%"=="y" ^(
echo     echo Uninstall cancelled
echo     pause
echo     exit /b 0
echo ^)
echo echo.
echo echo Removing virtual environment...
echo if exist "flash_data_logger_env" ^(
echo     rmdir /s /q "flash_data_logger_env"
echo     echo Virtual environment removed
echo ^) else ^(
echo     echo Virtual environment not found
echo ^)
echo echo.
echo echo Removing cache directory...
echo if exist "cache" ^(
echo     rmdir /s /q "cache"
echo     echo Cache directory removed
echo ^) else ^(
echo     echo Cache directory not found
echo ^)
echo echo.
echo echo Flash Data Logger v0.9 has been uninstalled
echo echo.
echo echo Note: This does not remove:
echo echo - Python installation
echo echo - PicoSDK installation
echo echo - Any CSV files you have saved
echo echo.
echo pause
) > "uninstall_flash_data_logger.bat"

echo.
echo Distribution package created successfully!
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
echo - Automated installer (install_flash_data_logger.bat)
echo - Application launcher (run_flash_data_logger.bat)
echo - Comprehensive documentation
echo - Installation verification script
echo - Uninstaller script
echo.
echo To distribute:
echo 1. Zip the %DIST_DIR% folder
echo 2. Share the zip file with users
echo 3. Users extract and run install_flash_data_logger.bat
echo.
echo Installation instructions:
echo - Users should read PREREQUISITES.md first
echo - Then run install_flash_data_logger.bat
echo - Finally run run_flash_data_logger.bat to launch
echo.

cd ..

echo Distribution package ready: %DIST_DIR%
echo.
pause

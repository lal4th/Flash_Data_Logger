# Flash Data Logger v0.9 - PowerShell Installer
# This is a PowerShell-based installer that may be more robust

param(
    [switch]$Force
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Function to write colored output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Function to check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to find source directory
function Find-SourceDirectory {
    Write-ColorOutput "[DIAGNOSTIC] Determining source files location..." "Yellow"
    
    $currentDir = Get-Location
    Write-ColorOutput "[DIAGNOSTIC] Current directory: $currentDir" "Gray"
    
    # Check current directory
    $appPath = Join-Path $currentDir "app"
    $requirementsPath = Join-Path $currentDir "requirements.txt"
    
    if ((Test-Path $appPath) -and (Test-Path $requirementsPath)) {
        Write-ColorOutput "[OK] Found source files in current directory: $currentDir" "Green"
        return $currentDir
    }
    
    # Check parent directory
    $parentDir = Split-Path $currentDir -Parent
    $parentAppPath = Join-Path $parentDir "app"
    $parentRequirementsPath = Join-Path $parentDir "requirements.txt"
    
    if ((Test-Path $parentAppPath) -and (Test-Path $parentRequirementsPath)) {
        Write-ColorOutput "[OK] Found source files in parent directory: $parentDir" "Green"
        return $parentDir
    }
    
    # If not found, show detailed diagnostic information
    Write-ColorOutput "[ERROR] Application files not found!" "Red"
    Write-ColorOutput "" "White"
    Write-ColorOutput "[DIAGNOSTIC] The installer is looking for the 'app' directory and 'requirements.txt' in:" "Yellow"
    Write-ColorOutput "- Current directory: $currentDir" "Gray"
    Write-ColorOutput "- Parent directory: $parentDir" "Gray"
    Write-ColorOutput "" "White"
    Write-ColorOutput "[DIAGNOSTIC] Current directory contents:" "Yellow"
    Get-ChildItem $currentDir | ForEach-Object { Write-ColorOutput "  $($_.Name)" "Gray" }
    Write-ColorOutput "" "White"
    Write-ColorOutput "[DIAGNOSTIC] Parent directory contents:" "Yellow"
    Get-ChildItem $parentDir | ForEach-Object { Write-ColorOutput "  $($_.Name)" "Gray" }
    Write-ColorOutput "" "White"
    Write-ColorOutput "[DIAGNOSTIC] Please ensure this installer is run from the correct location:" "Yellow"
    Write-ColorOutput "- Either from the root Flash Data Logger directory" "Gray"
    Write-ColorOutput "- Or from the FlashDataLogger_v0.9_Simple directory" "Gray"
    
    throw "Required files not found"
}

# Main installation function
function Install-FlashDataLogger {
    Write-ColorOutput "========================================" "Cyan"
    Write-ColorOutput "Flash Data Logger v0.9 - PowerShell Installer" "Cyan"
    Write-ColorOutput "========================================" "Cyan"
    Write-ColorOutput "" "White"
    
    # Check for administrator rights
    Write-ColorOutput "[DIAGNOSTIC] Checking for administrator rights..." "Yellow"
    if (-not (Test-Administrator)) {
        Write-ColorOutput "[ERROR] Administrator rights required!" "Red"
        Write-ColorOutput "" "White"
        Write-ColorOutput "Please run PowerShell as Administrator and try again." "Yellow"
        Write-ColorOutput "Right-click PowerShell and select 'Run as administrator'" "Yellow"
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-ColorOutput "[OK] Administrator rights confirmed." "Green"
    Write-ColorOutput "" "White"
    
    # Set installation directory
    $installDir = Join-Path $env:ProgramFiles "Flash Data Logger"
    Write-ColorOutput "[DIAGNOSTIC] Installation directory: $installDir" "Yellow"
    Write-ColorOutput "" "White"
    
    # Check if Python is installed
    Write-ColorOutput "[DIAGNOSTIC] Checking for Python..." "Yellow"
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found"
        }
        Write-ColorOutput "[OK] Python found: $pythonVersion" "Green"
    }
    catch {
        Write-ColorOutput "[ERROR] Python is not installed or not in PATH" "Red"
        Write-ColorOutput "" "White"
        Write-ColorOutput "Please install Python 3.8+ from https://python.org" "Yellow"
        Write-ColorOutput "Make sure to check 'Add Python to PATH' during installation" "Yellow"
        Write-ColorOutput "" "White"
        Write-ColorOutput "After installing Python, run this installer again." "Yellow"
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-ColorOutput "" "White"
    
    # Create installation directory
    Write-ColorOutput "[DIAGNOSTIC] Creating installation directory..." "Yellow"
    if (-not (Test-Path $installDir)) {
        New-Item -ItemType Directory -Path $installDir -Force | Out-Null
        Write-ColorOutput "[OK] Installation directory created successfully" "Green"
    } else {
        Write-ColorOutput "[INFO] Installation directory already exists" "Yellow"
    }
    Write-ColorOutput "" "White"
    
    # Find source directory
    $sourceDir = Find-SourceDirectory
    Write-ColorOutput "" "White"
    
    # Copy application files
    Write-ColorOutput "[DIAGNOSTIC] Copying application files from: $sourceDir" "Yellow"
    Write-ColorOutput "" "White"
    
    # Copy app directory
    $sourceAppPath = Join-Path $sourceDir "app"
    $destAppPath = Join-Path $installDir "app"
    Write-ColorOutput "[DIAGNOSTIC] Copying app directory..." "Yellow"
    Copy-Item -Path $sourceAppPath -Destination $destAppPath -Recurse -Force
    Write-ColorOutput "[OK] Successfully copied app directory" "Green"
    
    # Copy scripts directory if it exists
    $sourceScriptsPath = Join-Path $sourceDir "scripts"
    if (Test-Path $sourceScriptsPath) {
        $destScriptsPath = Join-Path $installDir "scripts"
        Write-ColorOutput "[DIAGNOSTIC] Copying scripts directory..." "Yellow"
        Copy-Item -Path $sourceScriptsPath -Destination $destScriptsPath -Recurse -Force
        Write-ColorOutput "[OK] Successfully copied scripts directory" "Green"
    }
    
    # Copy configuration files
    Write-ColorOutput "[DIAGNOSTIC] Copying configuration files..." "Yellow"
    $configFiles = @("requirements.txt", "setup.py", "pyproject.toml", "MANIFEST.in", "LICENSE", "README.md", "PREREQUISITES.md")
    
    foreach ($file in $configFiles) {
        $sourceFile = Join-Path $sourceDir $file
        if (Test-Path $sourceFile) {
            Copy-Item -Path $sourceFile -Destination $installDir -Force
            Write-ColorOutput "[OK] Copied $file" "Green"
        }
    }
    
    Write-ColorOutput "[OK] Application files copied successfully." "Green"
    Write-ColorOutput "" "White"
    
    # Create virtual environment
    Write-ColorOutput "[DIAGNOSTIC] Creating Python virtual environment..." "Yellow"
    $venvPath = Join-Path $installDir "venv"
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "[ERROR] Failed to create virtual environment" "Red"
        Write-ColorOutput "[DIAGNOSTIC] This may be due to insufficient permissions or Python issues." "Yellow"
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-ColorOutput "[OK] Virtual environment created successfully." "Green"
    Write-ColorOutput "" "White"
    
    # Install dependencies
    Write-ColorOutput "[DIAGNOSTIC] Installing Python dependencies..." "Yellow"
    Write-ColorOutput "[INFO] This may take a few minutes..." "Yellow"
    
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    & $activateScript
    
    Write-ColorOutput "[DIAGNOSTIC] Upgrading pip..." "Yellow"
    python -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "[WARNING] Failed to upgrade pip, continuing with current version" "Yellow"
    } else {
        Write-ColorOutput "[OK] Pip upgraded successfully" "Green"
    }
    
    $requirementsPath = Join-Path $installDir "requirements.txt"
    Write-ColorOutput "[DIAGNOSTIC] Installing dependencies from requirements.txt..." "Yellow"
    pip install -r $requirementsPath
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "[ERROR] Failed to install dependencies" "Red"
        Write-ColorOutput "[DIAGNOSTIC] This may be due to network issues or missing packages." "Yellow"
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-ColorOutput "[OK] Dependencies installed successfully" "Green"
    
    Write-ColorOutput "[DIAGNOSTIC] Installing Flash Data Logger package..." "Yellow"
    pip install $installDir
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "[WARNING] Package installation failed, but dependencies are installed" "Yellow"
        Write-ColorOutput "[INFO] The application may still work." "Yellow"
    } else {
        Write-ColorOutput "[OK] Package installed successfully" "Green"
    }
    
    Write-ColorOutput "[OK] Dependencies installed successfully." "Green"
    Write-ColorOutput "" "White"
    
    # Create launcher script
    Write-ColorOutput "[DIAGNOSTIC] Creating launcher script..." "Yellow"
    $launcherPath = Join-Path $installDir "FlashDataLogger.bat"
    $launcherContent = @"
@echo off
title Flash Data Logger v0.9
cd /d "$installDir"
call venv\Scripts\activate.bat
python -m app.main
if errorlevel 1 (
    echo.
    echo Application encountered an error.
    echo Please check that PicoScope 4262 is connected and PicoSDK is installed.
    echo See PREREQUISITES.md for troubleshooting.
    echo.
    pause
)
"@
    Set-Content -Path $launcherPath -Value $launcherContent
    Write-ColorOutput "[OK] Launcher script created." "Green"
    Write-ColorOutput "" "White"
    
    # Create desktop shortcut
    Write-ColorOutput "[DIAGNOSTIC] Creating desktop shortcut..." "Yellow"
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Flash Data Logger.lnk")
    $Shortcut.TargetPath = $launcherPath
    $Shortcut.WorkingDirectory = $installDir
    $Shortcut.Description = "Flash Data Logger v0.9 - PicoScope Data Acquisition"
    $Shortcut.Save()
    Write-ColorOutput "[OK] Desktop shortcut created successfully." "Green"
    
    # Create start menu shortcut
    Write-ColorOutput "[DIAGNOSTIC] Creating start menu entry..." "Yellow"
    $startMenuDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Flash Data Logger"
    if (-not (Test-Path $startMenuDir)) {
        New-Item -ItemType Directory -Path $startMenuDir -Force | Out-Null
    }
    $StartMenuShortcut = $WshShell.CreateShortcut("$startMenuDir\Flash Data Logger.lnk")
    $StartMenuShortcut.TargetPath = $launcherPath
    $StartMenuShortcut.WorkingDirectory = $installDir
    $StartMenuShortcut.Description = "Flash Data Logger v0.9 - PicoScope Data Acquisition"
    $StartMenuShortcut.Save()
    Write-ColorOutput "[OK] Start menu entry created successfully." "Green"
    
    # Create uninstaller
    Write-ColorOutput "[DIAGNOSTIC] Creating uninstaller..." "Yellow"
    $uninstallerPath = Join-Path $installDir "uninstall.bat"
    $uninstallerContent = @"
@echo off
title Flash Data Logger v0.9 - Uninstaller
echo ========================================
echo Flash Data Logger v0.9 - Uninstaller
echo ========================================
echo.
echo This will remove Flash Data Logger v0.9 from your system.
echo.
set /p confirm="Are you sure you want to uninstall? (y/N): "
if /i not "%confirm%"=="y" (
    echo Uninstall cancelled
    pause
    exit /b 0
)
echo.
echo Removing application files...
rmdir /s /q "$installDir"
echo.
echo Removing shortcuts...
del "$env:USERPROFILE\Desktop\Flash Data Logger.lnk" 2>nul
rmdir /s /q "$startMenuDir" 2>nul
echo.
echo Flash Data Logger v0.9 has been uninstalled successfully.
echo.
pause
"@
    Set-Content -Path $uninstallerPath -Value $uninstallerContent
    Write-ColorOutput "[OK] Uninstaller created." "Green"
    Write-ColorOutput "" "White"
    
    Write-ColorOutput "========================================" "Cyan"
    Write-ColorOutput "Installation Complete!" "Cyan"
    Write-ColorOutput "========================================" "Cyan"
    Write-ColorOutput "" "White"
    Write-ColorOutput "[OK] Flash Data Logger v0.9 has been installed successfully!" "Green"
    Write-ColorOutput "" "White"
    Write-ColorOutput "[INFO] Installation location: $installDir" "Yellow"
    Write-ColorOutput "[INFO] Desktop shortcut: Flash Data Logger" "Yellow"
    Write-ColorOutput "[INFO] Start menu: Flash Data Logger" "Yellow"
    Write-ColorOutput "" "White"
    Write-ColorOutput "[INFO] IMPORTANT NEXT STEPS:" "Yellow"
    Write-ColorOutput "1. Install PicoSDK from Pico Technology website" "Gray"
    Write-ColorOutput "2. Connect PicoScope 4262 via USB" "Gray"
    Write-ColorOutput "3. Close PicoScope desktop application" "Gray"
    Write-ColorOutput "4. Double-click desktop shortcut to launch" "Gray"
    Write-ColorOutput "" "White"
    Write-ColorOutput "[INFO] For troubleshooting, see PREREQUISITES.md in the installation directory." "Yellow"
    Write-ColorOutput "[INFO] To uninstall: Run uninstall.bat in the installation directory" "Yellow"
    Write-ColorOutput "" "White"
    
    # Ask if user wants to launch the application
    $launch = Read-Host "Would you like to launch Flash Data Logger now? (y/N)"
    if ($launch -eq "y" -or $launch -eq "Y") {
        Write-ColorOutput "" "White"
        Write-ColorOutput "[INFO] Launching Flash Data Logger..." "Yellow"
        Start-Process $launcherPath
    }
    
    Write-ColorOutput "" "White"
    Write-ColorOutput "[OK] Thank you for installing Flash Data Logger v0.9!" "Green"
    Read-Host "Press Enter to exit"
}

# Run the installation
try {
    Install-FlashDataLogger
}
catch {
    Write-ColorOutput "[ERROR] Installation failed: $($_.Exception.Message)" "Red"
    Read-Host "Press Enter to exit"
    exit 1
}

# Flash Data Logger v0.9 - Simple Installer Guide

## 🎯 **One-Click Installation**

The simple installer creates a single `.exe` file that handles everything automatically - no command line needed!

## 📦 **What the Simple Installer Does**

### **Automatic Installation**
- ✅ **Installs to Program Files** - Professional installation location
- ✅ **Creates Python virtual environment** - Isolated dependencies
- ✅ **Installs all dependencies** - PyQt6, numpy, picosdk, etc.
- ✅ **Creates desktop shortcut** - Double-click to launch
- ✅ **Adds to Start Menu** - Professional Windows integration
- ✅ **Windows uninstaller** - Clean removal via Programs & Features

### **User Experience**
- **Single .exe file** - Easy to download and share
- **Double-click to install** - No technical knowledge required
- **Desktop shortcut** - Launch with one click
- **Professional integration** - Appears in Windows Programs list

## 🚀 **Creating the Simple Installer**

### **Prerequisites**
- **NSIS (Nullsoft Scriptable Install System)** must be installed
- Download from: https://nsis.sourceforge.io/Download
- Or install via winget: `winget install NSIS.NSIS`

### **Build the Installer**
1. **Run the installer creator**:
   ```cmd
   create_simple_installer.bat
   ```

2. **This creates**: `FlashDataLogger_v0.9_Installer.exe`

3. **Distribute**: Share the single .exe file with users

## 👥 **For End Users**

### **Installation Process**
1. **Download** `FlashDataLogger_v0.9_Installer.exe`
2. **Double-click** the installer
3. **Follow prompts** (accept admin permissions)
4. **Wait for installation** (automatic Python setup)
5. **Done!** - Desktop shortcut created

### **Launching the Application**
- **Double-click** desktop shortcut "Flash Data Logger"
- **Or** find in Start Menu under "Flash Data Logger"
- **Or** use Programs & Features to uninstall

### **Prerequisites for Users**
- **Windows 10/11** (64-bit)
- **Python 3.8+** (installer will prompt if missing)
- **PicoScope 4262** connected via USB
- **PicoSDK** installed separately
- **Administrator rights** (for installation only)

## 🔧 **Technical Details**

### **Installation Location**
- **Program Files**: `C:\Program Files\Flash Data Logger\`
- **Virtual Environment**: `C:\Program Files\Flash Data Logger\venv\`
- **Desktop Shortcut**: Links to launcher script
- **Start Menu**: Professional Windows integration

### **What Gets Installed**
- Complete Flash Data Logger v0.9 application
- Python virtual environment with all dependencies
- Desktop and Start Menu shortcuts
- Windows uninstaller integration
- Launcher script for easy execution

### **Dependencies Handled Automatically**
- PyQt6 (GUI framework)
- pyqtgraph (plotting)
- numpy (numerical computing)
- picosdk (PicoScope API)
- pandas, scipy, and all other requirements

## 🚨 **Troubleshooting**

### **Common Issues**

#### **"NSIS not found" error**
- **Solution**: Install NSIS from https://nsis.sourceforge.io/Download
- **Or**: `winget install NSIS.NSIS`

#### **"Python not found" during installation**
- **Solution**: Install Python 3.8+ from https://python.org
- **Important**: Check "Add Python to PATH" during installation

#### **"Administrator rights required"**
- **Solution**: Right-click installer → "Run as administrator"

#### **Installation fails**
- **Check**: Python is installed and in PATH
- **Check**: Internet connection (for downloading dependencies)
- **Check**: Antivirus isn't blocking the installer

### **Manual Installation Fallback**
If the simple installer fails, users can still use the manual method:
1. Extract the distribution package
2. Run `install_flash_data_logger.bat`
3. Use `run_flash_data_logger.bat` to launch

## 📊 **Comparison: Simple vs Manual Installer**

| Feature | Simple Installer | Manual Installer |
|---------|------------------|------------------|
| **User Experience** | One-click install | Command line required |
| **Technical Knowledge** | None required | Basic command line |
| **Installation Location** | Program Files | User directory |
| **Windows Integration** | Full (shortcuts, uninstaller) | Basic |
| **Dependencies** | Automatic | Manual setup |
| **Distribution** | Single .exe file | Folder with scripts |
| **Professional** | Yes | No |

## 🎉 **Benefits of Simple Installer**

### **For Distributors**
- **Single file distribution** - Easy to share
- **Professional appearance** - Windows-standard installer
- **Automatic dependency handling** - No user configuration
- **Clean uninstallation** - Proper Windows integration

### **For End Users**
- **No technical knowledge required** - Just double-click
- **Professional installation** - Appears in Programs list
- **Easy launching** - Desktop shortcut
- **Clean removal** - Standard Windows uninstaller

## 📁 **File Structure After Installation**

```
C:\Program Files\Flash Data Logger\
├── app\                          # Application code
├── scripts\                      # Utility scripts
├── venv\                         # Python virtual environment
├── FlashDataLogger.bat           # Launcher script
├── requirements.txt              # Dependencies list
├── setup.py                      # Package configuration
├── README.md                     # Documentation
└── uninstall.exe                 # Windows uninstaller
```

## 🚀 **Quick Start for Users**

1. **Download** `FlashDataLogger_v0.9_Installer.exe`
2. **Double-click** to install
3. **Connect** PicoScope 4262 via USB
4. **Install** PicoSDK separately
5. **Double-click** desktop shortcut to launch
6. **Add plots** and start data acquisition

---

**The simple installer provides a professional, user-friendly installation experience that requires no technical knowledge from end users.**

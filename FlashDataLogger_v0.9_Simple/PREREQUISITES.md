# Flash Data Logger v0.9 - Prerequisites Guide

This guide covers all the prerequisites needed to install and run Flash Data Logger v0.9 on a Windows 11 computer.

## 🖥️ **System Requirements**

### **Operating System**
- **Windows 10** (version 1903 or later) or **Windows 11**
- **64-bit architecture** (x64)
- **Administrator privileges** (for driver installation)

### **Hardware Requirements**
- **PicoScope 4262** oscilloscope connected via USB
- **USB 2.0 or 3.0 port** (USB 3.0 recommended for best performance)
- **Minimum 4GB RAM** (8GB recommended)
- **500MB free disk space** for installation and data storage

## 🐍 **Python Requirements**

### **Python Installation**
1. **Download Python 3.8+** from [python.org](https://www.python.org/downloads/)
2. **Important**: During installation, check **"Add Python to PATH"**
3. **Verify installation**:
   ```cmd
   python --version
   pip --version
   ```

### **Supported Python Versions**
- Python 3.8.x
- Python 3.9.x
- Python 3.10.x
- Python 3.11.x

## 🔌 **PicoScope Hardware Setup**

### **1. PicoScope 4262 Connection**
- Connect PicoScope 4262 to computer via USB cable
- Ensure device is powered on (LED indicators should be active)
- Wait for Windows to recognize the device

### **2. PicoSDK Installation**
**CRITICAL**: PicoSDK must be installed before running Flash Data Logger

#### **Download PicoSDK**
1. Go to [Pico Technology Downloads](https://www.picotech.com/downloads)
2. Download **"PicoSDK"** (latest version)
3. Choose the **Windows 64-bit** version

#### **Install PicoSDK**
1. **Run installer as Administrator**
2. **Accept all default settings**
3. **Install to default location**: `C:\Program Files\Pico Technology\`
4. **Restart computer** after installation

#### **Verify PicoSDK Installation**
Check that these files exist:
```
C:\Program Files\Pico Technology\PicoSDK\lib\ps4000.dll
C:\Program Files\Pico Technology\PicoSDK\lib\ps4000a.dll
C:\Program Files\Pico Technology\PicoSDK\lib\ps5000.dll
```

### **3. Device Drivers**
PicoSDK installation should automatically install device drivers. If not:

#### **Manual Driver Installation**
1. Open **Device Manager**
2. Look for **"PicoScope 4000 Series"** under **"Universal Serial Bus devices"**
3. If device shows with warning icon:
   - Right-click → **"Update driver"**
   - Choose **"Browse my computer for drivers"**
   - Navigate to: `C:\Program Files\Pico Technology\PicoSDK\drivers\`
   - Click **"Next"** and follow prompts

## 🚫 **Important: Close PicoScope Desktop Application**

**CRITICAL**: The PicoScope desktop application must be closed before running Flash Data Logger.

### **Why This is Required**
- PicoScope devices can only be accessed by one application at a time
- Flash Data Logger uses direct API access to the device
- Having both applications open will cause connection conflicts

### **How to Close PicoScope**
1. **Check system tray** (bottom-right corner) for PicoScope icon
2. **Right-click PicoScope icon** → **"Exit"**
3. **Check Task Manager** for any remaining PicoScope processes:
   - Press `Ctrl + Shift + Esc`
   - Look for **"PicoScope.exe"** in Processes tab
   - End task if found

## 📦 **Python Package Dependencies**

Flash Data Logger requires these Python packages (automatically installed):

### **Core Dependencies**
- **PyQt6** (6.9.1) - GUI framework
- **pyqtgraph** (0.13.7) - Real-time plotting
- **numpy** (2.3.3) - Numerical computations
- **picosdk** (1.1) - PicoScope API wrapper
- **pandas** (2.3.2) - Data manipulation
- **scipy** (1.16.2) - Scientific computing

### **Supporting Dependencies**
- **pydantic** (2.11.7) - Data validation
- **python-dateutil** (2.9.0) - Date/time utilities
- **pytz** (2025.2) - Timezone support

## 🔧 **Installation Verification**

### **1. Test Python Installation**
```cmd
python --version
pip --version
```

### **2. Test PicoScope Connection**
After installing Flash Data Logger, run the connectivity test:
```cmd
cd "path\to\flash\data\logger"
flash_data_logger_env\Scripts\activate.bat
python scripts\pico_smoketest.py
```

### **3. Test Flash Data Logger**
```cmd
flash-data-logger
```

## 🚨 **Troubleshooting Common Issues**

### **Issue: "Python is not recognized"**
**Solution**: 
- Reinstall Python with "Add Python to PATH" checked
- Or manually add Python to PATH environment variable

### **Issue: "PicoScope not detected"**
**Solutions**:
1. **Check USB connection** - try different USB port
2. **Verify PicoSDK installation** - reinstall if necessary
3. **Close PicoScope desktop app** - ensure it's completely closed
4. **Check device drivers** - update in Device Manager
5. **Restart computer** - sometimes required after driver installation

### **Issue: "Permission denied" errors**
**Solution**: 
- Run Command Prompt as Administrator
- Or install to user directory instead of system directory

### **Issue: "Module not found" errors**
**Solutions**:
1. **Activate virtual environment**: `flash_data_logger_env\Scripts\activate.bat`
2. **Reinstall package**: `pip install -e .`
3. **Check Python version compatibility**

### **Issue: "DLL not found" errors**
**Solutions**:
1. **Verify PicoSDK installation** - check DLL files exist
2. **Add PicoSDK to PATH**:
   - Add `C:\Program Files\Pico Technology\PicoSDK\lib` to PATH
   - Restart Command Prompt
3. **Reinstall PicoSDK** as Administrator

### **Issue: Application crashes on startup**
**Solutions**:
1. **Check PicoScope connection** - ensure device is connected and recognized
2. **Close PicoScope desktop app** - completely exit all PicoScope processes
3. **Run connectivity test** - `python scripts\pico_smoketest.py`
4. **Check Windows Event Viewer** for detailed error messages

## 📞 **Getting Help**

### **Before Asking for Help**
1. **Run the connectivity test**: `python scripts\pico_smoketest.py`
2. **Check this prerequisites guide** thoroughly
3. **Verify all requirements** are met
4. **Try restarting** the computer

### **Information to Provide**
When seeking help, please provide:
- **Windows version** (Windows 10/11, build number)
- **Python version** (`python --version`)
- **PicoScope model** (4262)
- **PicoSDK version** (check in Programs and Features)
- **Error messages** (exact text)
- **Connectivity test results**

### **Support Resources**
- **GitHub Issues**: [Flash Data Logger Issues](https://github.com/lal4th/Flash_Data_Logger/issues)
- **Pico Technology Support**: [Pico Support](https://www.picotech.com/support)
- **Python Documentation**: [Python.org](https://docs.python.org/)

## ✅ **Installation Checklist**

Before running Flash Data Logger, verify:

- [ ] **Windows 10/11** (64-bit)
- [ ] **Python 3.8+** installed with PATH
- [ ] **PicoScope 4262** connected via USB
- [ ] **PicoSDK** installed and verified
- [ ] **Device drivers** installed (check Device Manager)
- [ ] **PicoScope desktop app** completely closed
- [ ] **Flash Data Logger** installed successfully
- [ ] **Connectivity test** passes
- [ ] **Application launches** without errors

## 🎯 **Quick Start After Installation**

1. **Connect PicoScope 4262** to USB port
2. **Close PicoScope desktop application** completely
3. **Run launcher**: Double-click `run_flash_data_logger.bat`
4. **Add plots**: Click "Add Plot" to configure channels
5. **Start acquisition**: Click "Start" to begin data logging

---

**Note**: This guide covers the most common installation scenarios. For specific hardware configurations or advanced troubleshooting, please refer to the Pico Technology documentation or contact support.

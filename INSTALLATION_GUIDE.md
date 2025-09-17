# Flash Data Logger v0.9 - Installation Guide

This guide provides step-by-step instructions for installing Flash Data Logger v0.9 as a standalone package on Windows 11.

## 📦 **Package Contents**

The Flash Data Logger v0.9 package includes:

### **Core Files**
- `app/` - Main application code
- `scripts/` - Utility scripts and tests
- `requirements.txt` - Python dependencies
- `setup.py` - Package installation script
- `pyproject.toml` - Modern Python packaging configuration

### **Installation Scripts**
- `install_flash_data_logger.bat` - Automated Windows installer
- `run_flash_data_logger.bat` - Application launcher
- `PREREQUISITES.md` - Detailed prerequisites guide

### **Documentation**
- `README.md` - Main documentation
- `REQUIREMENTS.md` - Technical requirements
- `Handoff_to_v1.0.md` - Development documentation

## 🚀 **Installation Methods**

### **Method 1: Automated Installation (Recommended)**

#### **Step 1: Prerequisites**
1. **Install Python 3.8+** from [python.org](https://python.org/downloads/)
   - ✅ Check "Add Python to PATH" during installation
   - ✅ Verify installation: `python --version`

2. **Install PicoSDK** from [Pico Technology](https://www.picotech.com/downloads)
   - ✅ Download and install PicoSDK (Windows 64-bit)
   - ✅ Restart computer after installation
   - ✅ Verify installation: Check `C:\Program Files\Pico Technology\PicoSDK\`

3. **Connect PicoScope 4262**
   - ✅ Connect via USB cable
   - ✅ Ensure device is powered on
   - ✅ Close PicoScope desktop application

#### **Step 2: Install Flash Data Logger**
1. **Extract package** to desired location (e.g., `C:\FlashDataLogger\`)
2. **Open Command Prompt** as Administrator
3. **Navigate to package directory**:
   ```cmd
   cd C:\FlashDataLogger
   ```
4. **Run installer**:
   ```cmd
   install_flash_data_logger.bat
   ```
5. **Follow prompts** and wait for installation to complete

#### **Step 3: Launch Application**
1. **Double-click** `run_flash_data_logger.bat`
2. **Or use Command Prompt**:
   ```cmd
   run_flash_data_logger.bat
   ```

### **Method 2: Manual Installation**

#### **Step 1: Setup Environment**
```cmd
# Navigate to package directory
cd C:\FlashDataLogger

# Create virtual environment
python -m venv flash_data_logger_env

# Activate virtual environment
flash_data_logger_env\Scripts\activate.bat
```

#### **Step 2: Install Dependencies**
```cmd
# Upgrade pip
python -m pip install --upgrade pip

# Install package in development mode
pip install -e .
```

#### **Step 3: Verify Installation**
```cmd
# Test connectivity
python scripts\pico_smoketest.py

# Launch application
flash-data-logger
```

### **Method 3: Production Installation**

#### **For System-wide Installation**
```cmd
# Install globally (requires admin privileges)
pip install .

# Launch from anywhere
flash-data-logger
```

#### **For User Installation**
```cmd
# Install for current user only
pip install --user .

# Launch from anywhere
flash-data-logger
```

## 🔧 **Post-Installation Setup**

### **1. Test Device Connectivity**
```cmd
# Run connectivity test
python scripts\pico_smoketest.py
```

**Expected Output:**
```
✓ PicoScope 4262 detected and connected
✓ Device opened successfully
✓ Ready for data acquisition
```

### **2. Configure Application**
1. **Launch Flash Data Logger**
2. **Add plots** using "Add Plot" button
3. **Configure channels** (A, B, or Math)
4. **Set sample rate** and other parameters
5. **Test acquisition** by clicking "Start"

### **3. Create Desktop Shortcut (Optional)**
1. **Right-click** on `run_flash_data_logger.bat`
2. **Select** "Create shortcut"
3. **Drag shortcut** to Desktop
4. **Rename** to "Flash Data Logger"

## 🚨 **Troubleshooting Installation**

### **Common Installation Issues**

#### **Issue: "Python is not recognized"**
**Solution:**
1. Reinstall Python with "Add to PATH" checked
2. Or manually add Python to PATH:
   - Open System Properties → Environment Variables
   - Add `C:\Python39\` and `C:\Python39\Scripts\` to PATH
   - Restart Command Prompt

#### **Issue: "Permission denied" during installation**
**Solution:**
1. Run Command Prompt as Administrator
2. Or install to user directory:
   ```cmd
   pip install --user -e .
   ```

#### **Issue: "Package installation fails"**
**Solution:**
1. Check internet connection
2. Upgrade pip: `python -m pip install --upgrade pip`
3. Try installing dependencies manually:
   ```cmd
   pip install -r requirements.txt
   ```

#### **Issue: "PicoScope not detected"**
**Solution:**
1. Verify PicoSDK installation
2. Check USB connection
3. Close PicoScope desktop application
4. Run connectivity test: `python scripts\pico_smoketest.py`

### **Verification Checklist**

After installation, verify:

- [ ] **Python 3.8+** installed and accessible
- [ ] **Virtual environment** created successfully
- [ ] **Dependencies** installed without errors
- [ ] **PicoSDK** installed and verified
- [ ] **PicoScope 4262** connected and recognized
- [ ] **Connectivity test** passes
- [ ] **Application launches** without errors
- [ ] **Plots can be added** and configured
- [ ] **Data acquisition** works

## 📁 **Directory Structure After Installation**

```
FlashDataLogger/
├── app/                          # Application code
│   ├── main.py                   # Entry point
│   ├── ui/main_window.py         # GUI interface
│   ├── core/streaming_controller.py  # Data acquisition
│   ├── processing/math_engine.py # Math channel engine
│   └── ...
├── scripts/                      # Utility scripts
│   └── pico_smoketest.py        # Connectivity test
├── flash_data_logger_env/        # Virtual environment
│   ├── Scripts/
│   │   ├── activate.bat         # Environment activation
│   │   └── flash-data-logger.exe # Application launcher
│   └── ...
├── cache/                        # Data cache directory
├── install_flash_data_logger.bat # Installer script
├── run_flash_data_logger.bat     # Launcher script
├── requirements.txt              # Dependencies
├── setup.py                      # Package configuration
└── README.md                     # Documentation
```

## 🎯 **Quick Start After Installation**

1. **Connect PicoScope 4262** to USB port
2. **Close PicoScope desktop application**
3. **Run launcher**: `run_flash_data_logger.bat`
4. **Add plots**: Click "Add Plot" → Configure channels
5. **Start acquisition**: Click "Start" button
6. **View data**: Real-time plots with synchronized scrolling
7. **Save data**: Click "Save CSV to..." when done

## 📞 **Getting Help**

### **Before Seeking Help**
1. **Read PREREQUISITES.md** thoroughly
2. **Run connectivity test**: `python scripts\pico_smoketest.py`
3. **Check installation**: Verify all requirements are met
4. **Try restarting** computer and application

### **Support Resources**
- **📋 Prerequisites Guide**: [PREREQUISITES.md](PREREQUISITES.md)
- **🐛 GitHub Issues**: [Report problems](https://github.com/lal4th/Flash_Data_Logger/issues)
- **📚 Documentation**: [README.md](README.md)
- **🔧 Pico Technology Support**: [Pico Support](https://www.picotech.com/support)

---

**Note**: This installation guide covers the most common scenarios. For advanced configurations or specific hardware setups, please refer to the detailed documentation or contact support.

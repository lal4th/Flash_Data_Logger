# Flash Data Logger v0.8

**Production-ready** PC application for high-performance real-time data acquisition, display, and logging from PicoScope oscilloscopes, with mathematically accurate voltage conversion, multi-channel support, dynamic plot management, and optimized streaming architecture for the PicoScope 4262.

## 🚀 **Key Features (v0.8)**

- **Multi-Channel Acquisition**: Simultaneous Channel A and B data acquisition with synchronized timestamps
- **Mathematically Accurate Voltage Conversion**: Scientifically derived formula for precise measurements across all voltage ranges
- **High-Performance Streaming**: Multi-threaded architecture supporting up to 5000Hz sample rates
- **Real-time Data Acquisition**: Direct ps4000 API communication with block-based acquisition
- **Dynamic Plot Management**: Flexible grid-based plot system with configurable channels and math channels
- **Enhanced UI**: Minimalist controls with "Add Plot" functionality for custom plot configurations
- **Synchronized Scrolling**: All grid plots scroll together horizontally for coordinated time analysis
- **Mirror Windows**: Double-click any plot to open an independent copy in a separate window
- **Extended CSV Export**: Multi-channel format with both Channel A and B data in single file
- **Plot Configuration**: Per-plot settings for Y-axis range, color, title, and channel selection
- **Session Management**: Start, stop, reset with proper data clearing and CSV management
- **Hardware Reconfiguration**: Runtime parameter changes without device restart
- **Zero Offset Functionality**: Accurate baseline measurements with offset correction (programmatic access)
- **Backward Compatibility**: v0.6 functionality preserved exactly

## Quick Start

### Prerequisites
- Windows 10+
- PicoScope 4262 connected via USB
- PicoSDK installed
- **Important**: Close PicoScope desktop application before running

### Installation
```bash
git clone https://github.com/lal4th/Flash_Data_Logger.git
cd Flash_Data_Logger
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Usage
```bash
# Run the GUI application
.venv\Scripts\python.exe -m app.main

# Test device connectivity (run this first if having issues)
.venv\Scripts\python.exe scripts\pico_smoketest.py
```

## 🏗️ **Architecture**

### **Streaming Architecture (v0.5)**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Acquisition    │    │   Processing    │    │   CSV Writing   │
│     Thread      │───▶│     Thread      │───▶│     Thread      │
│                 │    │                 │    │                 │
│ • PicoDirect    │    │ • Data Queue    │    │ • Background    │
│ • Block Capture │    │ • Plot Queue    │    │ • Batch Writes  │
│ • 100Hz Rate    │    │ • RAM Buffer    │    │ • Auto Flush    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │   Plot Update   │
                    │     Thread      │
                    │                 │
                    │ • Fixed 10Hz    │
                    │ • Continuous    │
                    │ • Real-time     │
                    └─────────────────┘
```

### **Key Components**
- **Entry Point**: `app/main.py`
- **Streaming Controller**: `app/core/streaming_controller.py` (multi-threaded architecture)
- **Device Communication**: `app/acquisition/pico_direct.py` (direct ps4000 API)
- **GUI**: `app/ui/main_window.py` (PyQt6 interface)
- **Storage**: `app/storage/csv_writer.py` (asynchronous CSV writing)

## 📊 **Performance Metrics**

| Metric | v0.6 (Previous) | v0.7 (Current) | Improvement |
|--------|----------------|----------------|-------------|
| Max Sample Rate | 5000 Hz | 5000 Hz | **Maintained** |
| Multi-Channel Support | Single Channel | Dual Channel | **2x channels** |
| CSV Format | Single Channel | Multi-Channel | **Extended** |
| Voltage Accuracy | Mathematically Correct | Mathematically Correct | **Preserved** |
| Backward Compatibility | N/A | v0.6 Compatible | **100%** |
| Plot Update Rate | Fixed 10 Hz | Fixed 10 Hz | **Consistent** |
| Responsiveness | <100ms | <100ms | **Maintained** |
| Memory Usage | Controlled | Controlled | **Stable** |

## ✅ **Current Status (v0.8)**

### **Fully Functional**
- **Multi-channel acquisition** - Simultaneous Channel A and B data acquisition
- **High-performance streaming** - Multi-threaded architecture with queues
- **Real-time data acquisition** - Up to 5000Hz sample rates
- **Dynamic plot management** - Flexible grid-based plot system with configurable channels
- **Enhanced UI** - Minimalist controls with "Add Plot" functionality
- **Synchronized scrolling** - All grid plots scroll together horizontally
- **Mirror windows** - Double-click any plot to open independent copy
- **Extended CSV logging** - Multi-channel format with both channels
- **Plot configuration** - Per-plot settings for Y-axis range, color, title, and channel selection
- **Session management** - Proper start, stop, reset with data clearing
- **Hardware reconfiguration** - Runtime parameter changes
- **Accurate voltage scaling** - Mathematically correct conversion formulas
- **Memory management** - Controlled RAM usage with automatic flushing
- **Backward compatibility** - v0.6 functionality preserved exactly

### **✅ v0.8 Enhanced UI Features**
- **Dynamic plot grid** - Automatically resizes from 1x1 to 3x3 based on number of plots
- **Add Plot dialog** - Configure new plots with channel selection, Y-axis range, color, and title
- **Plot management** - Edit, delete, and reorder plots with dedicated controls
- **Synchronized scrolling** - All grid plots scroll together for coordinated time analysis
- **Mirror windows** - Independent plot windows that can scroll separately from grid
- **Single plot per channel** - Prevents conflicts by allowing only one Channel A and one Channel B plot
- **Control state management** - Proper enabling/disabling of controls during logging sessions

### **🎯 Next Development (v0.9) - Math Channel Functionality**

#### **Primary Goals for v0.9:**
1. **Math Channel Implementation**
   - Excel-style formula input for mathematical expressions
   - Real-time calculation using Channel A and B as variables
   - Support for up to 6 math channels (Math_1 through Math_6)
   - Formula validation and error handling

2. **Enhanced Formula Engine**
   - Basic operations (+, -, *, /, ^, sqrt, abs)
   - Trigonometric functions (sin, cos, tan, asin, acos, atan)
   - Logarithmic functions (log, ln, exp)
   - Statistical functions (avg, min, max, std)
   - Conditional logic (if-then-else)

3. **Extended Data Management**
   - Math channel data included in CSV exports
   - Formula definitions saved in CSV headers
   - Configuration profiles for math channel setups

## 📚 **Documentation**

- **Current Handoff**: `Handoff_to_v0.9.md` - Complete v0.8 enhanced UI and v0.9 math channel roadmap
- **Development History**: `Handoff_to_v0.6.md`, `Handoff_to_v0.5.md`, `Handoff_to_v0.4.md`, `Handoff_to_v0.3.md`, `Handoff_to_v0.2.md`
- **Requirements**: Complete specifications in `REQUIREMENTS.md`
- **Smoke Test**: Standalone connectivity validation in `scripts/pico_smoketest.py`

## 🛠️ **Troubleshooting**

### **Common Issues**
- **Device not detected**: Check USB connection and PicoSDK installation
- **±5V range saturation**: Use ±10V or ±20V ranges for accurate readings
- **Performance issues**: Close other applications and check system resources
- **High sample rate crashes**: Use streaming architecture (default in v0.5)

### **Support**
- **Connectivity Test**: Run `python scripts/pico_smoketest.py` first
- **Debug Mode**: Check console output for detailed status messages
- **Cache Management**: Clear cache directory if experiencing storage issues

## 🤝 **Contributing**

This is a production-ready application for PicoScope data acquisition with multi-channel support. See `Handoff_to_v0.8.md` for detailed technical documentation and v0.8 development priorities.

## 📄 **License**

[Add license information]

---

**Status**: v0.8 - **Production Ready** with dynamic plot management, synchronized scrolling, mirror windows, and high-performance streaming architecture up to 5000Hz

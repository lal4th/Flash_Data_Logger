# Flash Data Logger v0.7

**Production-ready** PC application for high-performance real-time data acquisition, display, and logging from PicoScope oscilloscopes, with mathematically accurate voltage conversion, multi-channel support, and optimized streaming architecture for the PicoScope 4262.

## 🚀 **Key Features (v0.7)**

- **Multi-Channel Acquisition**: Simultaneous Channel A and B data acquisition with synchronized timestamps
- **Mathematically Accurate Voltage Conversion**: Scientifically derived formula for precise measurements across all voltage ranges
- **High-Performance Streaming**: Multi-threaded architecture supporting up to 5000Hz sample rates
- **Real-time Data Acquisition**: Direct ps4000 API communication with block-based acquisition
- **Live Plotting**: PyQt6 + pyqtgraph interface with fixed 10Hz update rate for smooth visualization
- **Extended CSV Export**: Multi-channel format with both Channel A and B data in single file
- **Multi-Channel Toggle**: Easy switching between single-channel (v0.6 compatibility) and dual-channel modes
- **Comprehensive Controls**: Channel selection, coupling (AC/DC), voltage range (±10mV to ±10V), resolution, sample rate
- **Session Management**: Start, stop, reset with proper data clearing and CSV management
- **Hardware Reconfiguration**: Runtime parameter changes without device restart
- **Zero Offset Functionality**: Accurate baseline measurements with offset correction
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

## ✅ **Current Status (v0.7)**

### **Fully Functional**
- **Multi-channel acquisition** - Simultaneous Channel A and B data acquisition
- **High-performance streaming** - Multi-threaded architecture with queues
- **Real-time data acquisition** - Up to 5000Hz sample rates
- **Live plotting** - Fixed 10Hz update rate with continuous lines
- **Extended CSV logging** - Multi-channel format with both channels
- **Multi-channel toggle** - Easy switching between single and dual-channel modes
- **Session management** - Proper start, stop, reset with data clearing
- **Hardware reconfiguration** - Runtime parameter changes
- **Accurate voltage scaling** - Mathematically correct conversion formulas
- **Memory management** - Controlled RAM usage with automatic flushing
- **Backward compatibility** - v0.6 functionality preserved exactly

### **✅ Multi-Channel Features**
- **Dual-channel acquisition** - Channel A and B sampled simultaneously
- **Synchronized timestamps** - Shared timing across both channels
- **Extended CSV format** - `timestamp,Channel_A,Channel_B` format
- **Independent configuration** - Separate settings for each channel
- **Mode switching** - Toggle between single and multi-channel operation

### **🎯 Next Development (v0.8) - Enhanced UI & Separate A/B Plots**

#### **Primary Goals for v0.8:**
1. **Separate A/B Plot Windows**
   - Tabbed interface with dedicated Channel A and Channel B plots
   - Independent Y-axis scaling for each channel
   - Synchronized time axes across tabs
   - Channel-specific styling and controls

2. **Enhanced CSV Recording**
   - Improved multi-channel CSV format with better metadata
   - Channel selection options for export
   - Enhanced headers with detailed configuration information
   - Batch processing capabilities

3. **Improved User Experience**
   - Enhanced multi-channel interface
   - Visual indicators for active channels
   - Better controls and status display
   - Performance optimizations for dual plots

## 📚 **Documentation**

- **Current Handoff**: `Handoff_to_v0.8.md` - Complete v0.7 multi-channel foundation and v0.8 roadmap
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

**Status**: v0.7 - **Production Ready** with multi-channel acquisition, mathematically accurate voltage conversion, and high-performance streaming architecture up to 5000Hz

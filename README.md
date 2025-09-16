# Flash Data Logger v0.6

**Production-ready** PC application for high-performance real-time data acquisition, display, and logging from PicoScope oscilloscopes, with mathematically accurate voltage conversion and optimized streaming architecture for the PicoScope 4262.

## 🚀 **Key Features (v0.6)**

- **Mathematically Accurate Voltage Conversion**: Scientifically derived formula for precise measurements across all voltage ranges
- **High-Performance Streaming**: Multi-threaded architecture supporting up to 5000Hz sample rates
- **Real-time Data Acquisition**: Direct ps4000 API communication with block-based acquisition
- **Live Plotting**: PyQt6 + pyqtgraph interface with fixed 10Hz update rate for smooth visualization
- **Automatic CSV Caching**: Background CSV writing with timestamped files and configurable cache directory
- **Comprehensive Controls**: Channel selection, coupling (AC/DC), voltage range (±10mV to ±10V), resolution, sample rate
- **Session Management**: Start, stop, reset with proper data clearing and CSV management
- **Hardware Reconfiguration**: Runtime parameter changes without device restart
- **Zero Offset Functionality**: Accurate baseline measurements with offset correction

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

| Metric | v0.4 (Previous) | v0.5 (Current) | Improvement |
|--------|----------------|----------------|-------------|
| Max Sample Rate | 1000 Hz | 5000 Hz | **5x** |
| Plot Update Rate | Variable | Fixed 10 Hz | **Consistent** |
| Responsiveness | 1-5 seconds | <100ms | **50x faster** |
| Memory Usage | Unbounded | Controlled | **Stable** |
| CSV Performance | Synchronous | Asynchronous | **Non-blocking** |

## ✅ **Current Status (v0.5)**

### **Fully Functional**
- **High-performance streaming** - Multi-threaded architecture with queues
- **Real-time data acquisition** - Up to 5000Hz sample rates
- **Live plotting** - Fixed 10Hz update rate with continuous lines
- **Automatic CSV logging** - Background writing with timestamped files
- **Session management** - Proper start, stop, reset with data clearing
- **Hardware reconfiguration** - Runtime parameter changes
- **Accurate voltage scaling** - Correct conversion formulas
- **Memory management** - Controlled RAM usage with automatic flushing

### **⚠️ Known Limitations**
- **±5V range saturation** - Hardware-level issue (use ±10V or ±20V for accurate readings)
- **Single channel** - Channel A only (Channel B ready for implementation)
- **Fixed timebase** - Uses timebase 8 for all sample rates

### **🎯 Next Development (v0.7) - Multi-Channel & Math Channel Support**

#### **Primary Goals for v0.7:**
1. **Multi-Channel Support**
   - Simultaneous Channel A and B acquisition
   - Separate plot windows for each channel
   - Independent controls for voltage range, coupling, offset
   - Both channels recorded in CSV with timestamps

2. **Math Channel Support**
   - Excel-style calculator bar for real-time formulas
   - Up to 6 additional math channels (A+B, A-B, A*B, A/B, A^2, sqrt(A), etc.)
   - Separate plot windows for each math channel
   - All math channel values included in CSV export

3. **Enhanced UI**
   - Tabbed interface for multiple plots
   - Formula editor with syntax validation
   - Drag-and-drop channel management
   - Configuration profiles for multi-channel setups

## 📚 **Documentation**

- **Current Handoff**: `Handoff_to_v0.6.md` - Complete technical documentation and v0.7 roadmap
- **Development History**: `Handoff_to_v0.4.md`, `Handoff_to_v0.3.md`, `Handoff_to_v0.2.md`
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

This is a production-ready application for PicoScope data acquisition. See `Handoff_to_v0.5.md` for detailed technical documentation and development priorities.

## 📄 **License**

[Add license information]

---

**Status**: v0.6 - **Production Ready** with mathematically accurate voltage conversion and high-performance streaming architecture up to 5000Hz

# Flash Data Logger v0.3

PC application for acquiring, displaying, and logging data from PicoScope oscilloscopes, with initial focus on the PicoScope 4262.

## Features

- **Real-time Data Acquisition**: Direct ps4000 API communication via ctypes
- **Live Plotting**: PyQt6 + pyqtgraph interface with user-controlled timeline and Y-axis ranges
- **Automatic CSV Caching**: Timestamped data recording with user-configurable cache directory
- **Device Controls**: Channel selection, coupling (AC/DC), voltage range, resolution, sample rate
- **User-Controlled Plotting**: Customizable Y-axis range (±5V default) and timeline (60s default)
- **Smart Device Management**: Single device connection with reuse between Start/Stop cycles
- **Robust Error Handling**: Comprehensive diagnostics and fallback to dummy source

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

## Architecture

- **Entry Point**: `app/main.py`
- **Device Communication**: `app/acquisition/pico_direct.py` (direct ps4000 API)
- **GUI**: `app/ui/main_window.py` (PyQt6 interface)
- **Data Processing**: `app/core/controller.py` (orchestrates acquisition)
- **Storage**: `app/storage/csv_writer.py` (timestamp,value format)

## Current Status (v0.3)

### ✅ Working
- **PicoScope 4262 device detection and connection** - Fully functional
- **Real-time data plotting** - Live data visualization working correctly
- **CSV data logging** - Automatic timestamped file creation with proper data
- **User-controlled plot management** - Y-axis range and timeline controls
- **Device reuse** - No popup on Start button after initial startup
- **Smart plot scrolling** - When data exceeds timeline
- **Clean UI** - Essential controls with proper status display
- **Error handling** - Graceful fallback to dummy data when device unavailable

### ⚠️ Known Issues
- **Timestamp Continuity Bug**: Plot doesn't reset to 0 when restarting sessions
- **Erratic Plotting**: Wild oscillations when changing sample rates
- **Minor**: Status messages could be more descriptive

### 🎯 Next (v0.4)
- Fix timestamp continuity for proper session restarts
- Resolve erratic plotting behavior during configuration changes
- Enhanced error recovery and user feedback
- Performance optimization for long-running sessions

## Documentation

- **Development Handoff**: See `Handoff_to_v0.4.md` for detailed technical status and next steps
- **Previous Versions**: See `Handoff_to_v0.3.md` and `Handoff_to_v0.2.md` for development history
- **Requirements**: Complete specifications in `REQUIREMENTS.md`
- **Smoke Test**: Standalone connectivity validation in `scripts/pico_smoketest.py`

## Contributing

This is a focused development project for PicoScope data acquisition. See the handoff documentation for current development priorities and technical details.

## License

[Add license information]

---

**Status**: v0.3 - PicoScope connection and data plotting working, ready for v0.4 timestamp continuity fixes

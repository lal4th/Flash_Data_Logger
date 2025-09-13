# Flash Data Logger v0.2

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

## Current Status (v0.2)

### ✅ Working
- PicoScope 4262 device detection and connection
- User-controlled plot management (Y-axis range, timeline)
- Automatic CSV cache system with timestamped filenames
- Device reuse (no popup on Start button after initial startup)
- Smart plot scrolling when data exceeds timeline
- Clean UI with essential controls only
- Proper plot initialization with correct axis ranges

### ⚠️ Known Issues
- **CRITICAL**: No data plotting when Start button clicked (device connects but data doesn't appear)
- Some debug messages still appear in terminal
- Data acquisition loop may not be running properly

### 🎯 Next (v0.3)
- Debug and fix data plotting issue
- Clean up remaining terminal debug messages
- Validate CSV output contains proper data
- Add comprehensive data flow testing

## Documentation

- **Development Handoff**: See `Handoff_to_v0.3.md` for detailed technical status and next steps
- **Previous Version**: See `Handoff_to_v0.2.md` for v0.1 → v0.2 development history
- **Requirements**: Complete specifications in `REQUIREMENTS.md`
- **Smoke Test**: Standalone connectivity validation in `scripts/pico_smoketest.py`

## Contributing

This is a focused development project for PicoScope data acquisition. See the handoff documentation for current development priorities and technical details.

## License

[Add license information]

---

**Status**: v0.2 - UI improvements and device management complete, ready for v0.3 data plotting fixes

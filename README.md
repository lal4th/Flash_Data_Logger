# Flash Data Logger v0.1

PC application for acquiring, displaying, and logging data from PicoScope oscilloscopes, with initial focus on the PicoScope 4262.

## Features

- **Real-time Data Acquisition**: Direct ps4000 API communication via ctypes
- **Live Plotting**: PyQt6 + pyqtgraph interface with 30 FPS updates  
- **CSV Logging**: Timestamped data recording with configurable filename
- **Device Controls**: Channel selection, coupling (AC/DC), voltage range, resolution, sample rate
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

## Current Status (v0.1)

### ✅ Working
- PicoScope 4262 device detection and connection
- Live voltage data display with configurable ranges (±10mV to ±20V)
- Real-time plotting with reset functionality
- CSV data recording
- Comprehensive error diagnostics

### ⚠️ Known Issues
- CSV timestamps not properly calibrated (showing 1.137s intervals instead of expected 0.010s for 100Hz)
- PicoScope popup dialog appears on every Start click
- Sample rate display shows "0 Hz" in console

### 🎯 Next (v0.2)
- Fix timestamp calculation in block-mode acquisition
- Eliminate startup popup delays
- Add streaming mode for continuous logging
- Enhanced device-aware validation

## Documentation

- **Development Handoff**: See `Handoff_to_v0.2.md` for detailed technical status
- **Requirements**: Complete specifications in `REQUIREMENTS.md`
- **Smoke Test**: Standalone connectivity validation in `scripts/pico_smoketest.py`

## Contributing

This is a focused development project for PicoScope data acquisition. See the handoff documentation for current development priorities and technical details.

## License

[Add license information]

---

**Status**: v0.1 - Baseline connectivity established, ready for v0.2 enhancements

# Flash Data Logger v0.2 → v0.3 Handoff

## Project Overview
PC application to acquire, display, and log data from PicoScope 4262 oscilloscope using direct ps4000 API calls (ctypes). Built with PyQt6 + pyqtgraph on Windows 10+.

**Entry Point**: `.venv\Scripts\python.exe -m app.main`

## ✅ **MAJOR ACCOMPLISHMENTS (v0.2)**

### Phase 2A: Enhanced Data Acquisition ✅ COMPLETE
- **Reset Plot Button**: Added functional button to clear plot and restart timing
- **Improved Error Handling**: Buffer overflow detection, sample validation
- **Voltage Range Mapping**: Proper ADC→voltage conversion based on UI range setting (±10mV to ±20V)
- **Status**: UI improvements working, timestamp issues resolved

### Phase 2B: Plot Management & User Controls ✅ COMPLETE
- **User-Controlled Y-Axis**: Added Y-axis Max/Min spinbox controls (default ±5V)
- **User-Controlled Timeline**: Added Timeline spinbox control (default 60s)
- **Fixed Plot Initialization**: Plot now starts with correct axis ranges
- **Smart Scrolling**: Plot scrolls when data exceeds timeline length
- **Proper Reset**: Reset button resets both data and axis ranges

### Phase 2C: CSV Cache System ✅ COMPLETE
- **Automatic Cache Creation**: Always creates timestamped CSV files
- **Filename Format**: `Flash_Data_Logger_CSV_YYYY_MM_DD_HH.MM.SS.csv`
- **User-Configurable Cache Directory**: "CSV Cache" field with browse button
- **Manual Save Option**: "Save CSV to..." button copies cache to user location
- **Smart File Discovery**: Finds most recent cache file even after stopping

### Phase 2D: UI Cleanup & Improvements ✅ COMPLETE
- **Removed Redundant Controls**: Eliminated "Record to CSV" checkbox and "Filename" field
- **Cleaner Interface**: Simplified UI with only essential controls
- **Better Labels**: "CSV Cache" instead of "Cache Directory"
- **Improved Status Messages**: Clear feedback about device state and operations

### Phase 2E: Device Management ✅ COMPLETE
- **Device Reuse**: PicoScope opens once at startup, reused for Start/Stop cycles
- **Popup Elimination**: No more PicoScope loading dialog on every Start click
- **Persistent Connection**: Device stays open between acquisition sessions
- **Proper Cleanup**: Device closed only on application shutdown

## ⚠️ **KNOWN ISSUES (Critical for v0.3)**

### 1. **Data Plotting Issue** - HIGH PRIORITY
**Problem**: No data appears on plot when Start button is clicked
- Status shows: "Using Pico source (ps4000) - device reused"
- Device detection works (smoke test passes)
- No data points appear in status bar or on plot
- CSV files are created but may be empty

**Analysis**: 
- Device opens successfully at startup
- Device reuse works (no popup on Start)
- Data acquisition loop may not be running or data not reaching plot
- Need to debug the data flow from PicoDirectSource → Controller → UI

**Debug Approach**:
1. Add more detailed logging to data acquisition loop
2. Check if `_run_loop` is actually running
3. Verify data is being read from PicoDirectSource
4. Check if plot signals are being emitted
5. Test with dummy data source to isolate issue

### 2. **Terminal Debug Messages** - MEDIUM PRIORITY
**Problem**: Some debug messages still appear in terminal
- Shows "Info: Using calculated timebase 3 = 125000000 Hz (interval=0.000000008s)"
- Should be completely silent for clean operation

**Solution**: Remove remaining print statements from PicoDirectSource

## 🏗️ **CURRENT ARCHITECTURE**

### Core Components
- **`app/acquisition/pico_direct.py`**: Direct ps4000 implementation with device reuse
- **`app/core/controller.py`**: Orchestrates acquisition, handles device lifecycle
- **`app/ui/main_window.py`**: PyQt6 GUI with user controls and live plot
- **`app/storage/csv_writer.py`**: Handles CSV file creation and formatting
- **`scripts/pico_smoketest.py`**: Standalone connectivity validation

### Data Flow
1. Startup: `probe_device()` opens PicoScope once (popup acceptable)
2. Start: Reuses existing device, starts acquisition thread
3. Acquisition: `_run_loop()` reads data, updates plot, writes CSV
4. Display: Plot shows user-controlled timeline with smart scrolling
5. Stop: Preserves device connection, closes CSV writer
6. Shutdown: Closes device and cleans up resources

### Device Communication
- **DLL**: Found via recursive scan of `C:\Program Files\Pico Technology`
- **Initialization**: PATH setup, DLL loading, device opening, channel configuration
- **Block Mode**: Uses ps4000RunBlock → ps4000IsReady → ps4000GetValues cycle
- **Device Reuse**: Single device connection maintained throughout session

## 📋 **IMMEDIATE NEXT STEPS (v0.3 Priority)**

### 1. **Debug Data Plotting Issue** 🔥 CRITICAL
```python
# Add debugging to app/core/controller.py _run_loop():
def _run_loop(self) -> None:
    print("DEBUG: _run_loop started")
    # ... existing code ...
    try:
        value, timestamp = self._source.read()
        print(f"DEBUG: Read data: {value:.4f}V at {timestamp:.6f}s")
        # ... rest of processing ...
    except Exception as e:
        print(f"DEBUG: Data acquisition error: {e}")
```

**Debug Checklist**:
1. Verify `_run_loop` is running (add print at start)
2. Check if `self._source.read()` returns valid data
3. Confirm data reaches plot update logic
4. Test with DummySineSource to isolate PicoScope issue
5. Check if plot signals are being emitted and received

### 2. **Clean Up Debug Messages** 🔧 IMPORTANT
```python
# Remove remaining print statements from app/acquisition/pico_direct.py
# All console output should be eliminated for production use
```

### 3. **Validate CSV Output** ✅ VERIFY
Once data plotting is fixed, verify CSV contains:
- Timestamps starting at 0.000 seconds
- Proper increment (e.g., 0.000000008s for 125MHz)
- Voltage values in expected range
- Headers: `timestamp,value`

## 🎯 **MEDIUM-TERM ROADMAP**

### Phase 3A: Data Acquisition Validation
- Comprehensive data flow testing and validation
- Performance optimization for high sample rates
- Error recovery and reconnection logic

### Phase 3B: Enhanced Plot Features
- Zoom and pan controls
- Multiple channel support
- Real-time statistics display
- Export plot as image

### Phase 3C: Advanced CSV Features
- Multiple file formats (CSV, HDF5, etc.)
- Data compression options
- Metadata headers with device info
- Batch processing capabilities

### Phase 3D: User Experience
- Settings persistence
- Keyboard shortcuts
- Help system and documentation
- Multi-language support

## 🔧 **DEVELOPMENT ENVIRONMENT**

### Setup
- **OS**: Windows 10+
- **Python**: Virtual environment with requirements from `requirements.txt`
- **Hardware**: PicoScope 4262 connected via USB
- **SDK**: PicoSDK installed, PicoScope desktop app must be closed during use

### Key Files  
- **Entry**: `python -m app.main`
- **Smoke Test**: `python scripts/pico_smoketest.py` (always test this first!)
- **Requirements**: All deps in `requirements.txt`, no additional installs needed

### Testing Workflow
1. **Device Test**: Run smoke test to verify PicoScope connectivity
2. **App Test**: Run main application and check device detection
3. **Data Test**: Click Start and verify data appears on plot
4. **CSV Test**: Stop acquisition and test CSV save functionality

## 🚀 **CONTINUATION PROMPT FOR NEXT SESSION**

```
I'm continuing development of the Flash Data Logger v0.2 → v0.3. This is a Python PyQt6 app for PicoScope 4262 data acquisition.

CURRENT STATUS:
✅ Device connectivity working (PicoScope connects, no popup on Start)
✅ UI improvements complete (user controls, plot management, CSV cache)
✅ Device reuse implemented (single connection, proper cleanup)
⚠️ CRITICAL BUG: No data plotting when Start button clicked

PRIORITY FIXES NEEDED:
1. Debug data plotting issue - no data appears on plot despite device connection
2. Clean up remaining terminal debug messages
3. Verify CSV output contains proper data

WORKING TEST:
- Run: .venv\Scripts\python.exe scripts\pico_smoketest.py (should show 10 voltage samples)
- If that fails, check device connection/PicoScope app closed

CONTEXT: Device opens successfully at startup, reuse works, but data acquisition loop may not be running or data not reaching plot. Need to debug the data flow from PicoDirectSource through controller to UI.

Please review Handoff_to_v0.3.md and focus on debugging the data plotting issue first.
```

## 📊 **CURRENT STATE SUMMARY**

**✅ WORKS**: Device connection, UI controls, plot management, CSV cache system, device reuse  
**⚠️ BROKEN**: Data plotting (no data appears when Start clicked)  
**🎯 NEXT**: Debug data acquisition loop, verify data flow, clean up debug messages

**Ready for v0.3 development!** 🚀

## 🔍 **DEBUGGING NOTES**

### Data Flow Investigation
The issue appears to be in the data acquisition loop. The device connects successfully, but data may not be flowing through the system. Key areas to investigate:

1. **Controller._run_loop()**: Is this method actually running?
2. **PicoDirectSource.read()**: Is this returning valid data?
3. **Plot signal emission**: Are signals being sent to UI?
4. **UI signal handling**: Is the plot receiving and displaying data?

### Test Strategy
1. Add comprehensive logging to data flow
2. Test with DummySineSource to isolate PicoScope issues
3. Verify thread is running and not blocked
4. Check for exceptions in data acquisition loop

### Success Criteria for v0.3
- Data appears on plot when Start button clicked
- CSV files contain valid data
- Clean console output (no debug messages)
- Stable data acquisition for extended periods

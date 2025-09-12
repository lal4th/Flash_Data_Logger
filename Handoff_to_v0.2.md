# Flash Data Logger v0.1 → v0.2 Handoff

## Project Overview
PC application to acquire, display, and log data from PicoScope 4262 oscilloscope using direct ps4000 API calls (ctypes). Built with PyQt6 + pyqtgraph on Windows 10+.

**Entry Point**: `.venv\Scripts\python.exe -m app.main`

## ✅ **MAJOR ACCOMPLISHMENTS (v0.1)**

### Phase 0: Baseline Device Connectivity ✅ COMPLETE
- **Smoke Test**: `scripts/pico_smoketest.py` successfully proves end-to-end connectivity
  - Locates ps4000.dll via recursive scan of Pico Technology installation
  - Opens PicoScope 4262, configures Channel A (DC, ±5V), runs block capture
  - Retrieves 1000 samples, converts ADC→volts, prints first 10 values
  - Clean device shutdown with proper error handling
  - **Status**: PROVEN WORKING - prints voltage samples like -0.0078V to -0.0037V

### Phase 1: GUI Integration ✅ COMPLETE  
- **Fresh Implementation**: Created `app/acquisition/pico_direct.py` using ONLY proven smoke test approach
- **Reliable Block-Mode Source**: PicoDirectSource class with smart timebase selection
- **GUI Integration**: Successfully connects to PicoScope 4262 and displays live data
- **Error Handling**: Detailed status codes and DLL path diagnostics
- **Fallback System**: Graceful fallback to dummy source with exact error reporting
- **Status**: WORKING - GUI shows "Using Pico source (ps4000)" and live voltage plot

### Phase 2A: Enhanced Data Acquisition ✅ PARTIAL
- **Reset Plot Button**: Added functional button to clear plot and restart timing
- **Improved Error Handling**: Buffer overflow detection, sample validation
- **Voltage Range Mapping**: Proper ADC→voltage conversion based on UI range setting (±10mV to ±20V)
- **Status**: UI improvements working, but timestamp issues remain

## ⚠️ **KNOWN BUGS (Critical for v0.2)**

### 1. **CSV Timestamp Issue** - HIGH PRIORITY
**Problem**: CSV timestamps not in seconds as expected
- Current: Shows `interval=1.137181s` (way too long for 100Hz)
- Expected: Should be ~0.010s for 100Hz sampling
- Root cause: `time_interval_ns=1137180672` from ps4000GetTimebase2 is incorrect
- **Console Output**: `Debug: timebase=3, interval_ns=1137180672`

**Analysis**: 
- Timebase 3 should give ~8ns intervals, not 1.1 seconds
- ps4000GetTimebase2 is returning garbage data
- Fallback calculation not triggering properly

### 2. **PicoScope Popup on Start** - MEDIUM PRIORITY  
**Problem**: PicoScope loading dialog appears every time "Start" is clicked
- Should only appear once at startup (acceptable)
- Currently: Popup at startup AND every Start click
- User wants: Popup at startup only, no delays on Start

### 3. **Sample Rate Display** - LOW PRIORITY
**Problem**: Console shows "0 Hz" instead of actual sample rate
- Related to timestamp calculation bug above

## 🏗️ **CURRENT ARCHITECTURE**

### Core Components
- **`app/acquisition/pico_direct.py`**: Direct ps4000 implementation (proven working for connectivity)
- **`app/core/controller.py`**: Orchestrates acquisition, handles source selection
- **`app/ui/main_window.py`**: PyQt6 GUI with controls and live plot
- **`scripts/pico_smoketest.py`**: Standalone connectivity validation

### Data Flow
1. Startup: `test_device_connection()` validates DLL and device
2. Start: Creates `PicoDirectSource`, configures device, starts acquisition thread  
3. Acquisition: Captures 1000-sample blocks, converts to volts, streams sample-by-sample
4. Display: 30 FPS plot updates, CSV logging with timestamps
5. Stop: Clean device shutdown, thread termination

### Device Communication
- **DLL**: Found via recursive scan of `C:\Program Files\Pico Technology`
- **Initialization**: PATH setup, DLL loading, device opening, channel configuration
- **Block Mode**: Uses ps4000RunBlock → ps4000IsReady → ps4000GetValues cycle
- **Error Handling**: Comprehensive status code mapping and diagnostics

## 📋 **IMMEDIATE NEXT STEPS (v0.2 Priority)**

### 1. **Fix Timestamp Calculation** 🔥 CRITICAL
```python
# Current broken logic in _capture_block():
actual_interval_ns = time_interval_ns.value  # Returns 1137180672 (wrong!)
self._actual_sample_interval_s = actual_interval_ns / 1e9  # = 1.137s (wrong!)

# Need to investigate:
# - Is ps4000GetTimebase2 call structure correct?
# - Are ctypes parameter types correct? 
# - Should we use ps4000GetTimebase instead?
# - Is timebase selection algorithm wrong?
```

**Debug Approach**:
1. Compare with working smoke test (which doesn't use ps4000GetTimebase2)
2. Verify ctypes function signatures against documentation
3. Test with different timebase values
4. Consider using fixed intervals based on timebase math

### 2. **Eliminate Start Popup** 🔧 IMPORTANT
```python
# Current: Device opens fresh on every Start
# Target: Open device once at startup, reuse connection

# Strategies:
# - Keep device open between Start/Stop cycles
# - Move device initialization to startup probe
# - Add connection pooling/reuse logic
```

### 3. **Validate CSV Output** ✅ VERIFY
Once timestamps fixed, verify CSV contains:
- Timestamps starting at 0.000 seconds
- Proper increment (e.g., 0.010s for 100Hz) 
- Voltage values in expected range
- Headers: `timestamp,value`

## 🎯 **MEDIUM-TERM ROADMAP**

### Phase 2B: Enhanced Controls & Validation
- Device-aware sample rate clamping with user feedback
- Voltage range validation and limits
- Real-time sample rate reporting (actual vs requested)

### Phase 2C: Streaming Mode Foundation  
- Implement ps4000RunStreaming for continuous logging
- Callback-based data acquisition
- Compare block vs streaming performance

### Phase 2D: CSV Recording Enhancement
- Metadata headers (device info, settings)
- Robust file handling and error recovery  
- User-selectable CSV format options

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

### Memory Context [[memory:8854466]]
Target device is PicoScope 4262. Use continuous streaming first. UI must expose channel, coupling (AC/DC), input range, resolution, and sample rate with device-aware min/max validation. Plan to support other PicoScopes later.

## 🚀 **CONTINUATION PROMPT FOR NEXT SESSION**

```
I'm continuing development of the Flash Data Logger v0.1 → v0.2. This is a Python PyQt6 app for PicoScope 4262 data acquisition.

CURRENT STATUS:
✅ Basic connectivity working (PicoScope connects, displays live data)  
✅ GUI functional with reset button, voltage range selection
⚠️ CRITICAL BUG: CSV timestamps wrong (showing 1.137s intervals instead of 0.010s for 100Hz)
⚠️ ANNOYING: PicoScope popup appears on every Start click (should be startup only)

PRIORITY FIXES NEEDED:
1. Fix timestamp calculation in app/acquisition/pico_direct.py _capture_block() method
2. Eliminate Start button popup behavior  
3. Verify CSV output shows proper seconds-based timestamps

WORKING TEST:
- Run: .venv\Scripts\python.exe scripts\pico_smoketest.py (should show 10 voltage samples)
- If that fails, check device connection/PicoScope app closed

CONTEXT: Direct ps4000 API via ctypes, no Python wrappers. Working smoke test proves device connectivity. Issue is in ps4000GetTimebase2 returning wrong interval values.

Please review Handoff_to_v0.2.md and focus on fixing the timestamp calculation bug first.
```

## 📊 **CURRENT STATE SUMMARY**

**✅ WORKS**: Device connection, live data display, GUI controls, plot reset  
**⚠️ BROKEN**: CSV timestamps, Start button popup behavior  
**🎯 NEXT**: Fix timestamp math, eliminate popups, verify CSV output

**Ready for v0.2 development!** 🚀

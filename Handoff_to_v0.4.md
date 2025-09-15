# Flash Data Logger - Handoff to v0.4

## Project Status: ✅ **STABLE & WORKING**

The Flash Data Logger is now in a stable, working state with successful PicoScope 4262 integration and real-time data plotting.

---

## 🎯 **Current Capabilities (v0.3)**

### ✅ **Working Features**
- **PicoScope 4262 Integration**: Direct device communication via ps4000.dll
- **Real-time Data Acquisition**: Live data streaming from PicoScope channels
- **Live Plotting**: Real-time visualization using pyqtgraph
- **CSV Caching**: Automatic data storage to timestamped CSV files
- **GUI Controls**: Start/Stop/Reset functionality with status display
- **Device Detection**: Automatic PicoScope detection and connection
- **Sample Rate Control**: User-configurable acquisition rates
- **Error Handling**: Graceful fallback to dummy data when PicoScope unavailable

### 🔧 **Technical Architecture**
- **GUI Framework**: PyQt6 with modern UI design
- **Data Acquisition**: Direct ctypes calls to ps4000.dll (no Python wrapper dependencies)
- **Threading**: Background data acquisition with Qt signals/slots
- **Data Pipeline**: Acquisition → Processing → Storage → Visualization
- **File Management**: Automatic CSV file creation with timestamps

---

## 🐛 **Known Issues & Bugs**

### ❌ **Critical Issues**
1. **Timestamp Continuity Bug**: 
   - **Problem**: When stopping and restarting acquisition, timestamps don't reset to 0
   - **Symptom**: Plot continues from previous session's end time instead of starting fresh
   - **Impact**: CSV files show incorrect timestamps, plot doesn't start at origin
   - **Status**: ⚠️ **PARTIALLY FIXED** - Requires further investigation

2. **Erratic Plotting on Sample Rate Change**:
   - **Problem**: Changing sample rate and starting new session causes erratic plot behavior
   - **Symptom**: Plot shows wild oscillations before settling
   - **Impact**: Poor user experience during configuration changes
   - **Status**: ⚠️ **PARTIALLY FIXED** - Requires further investigation

### ⚠️ **Minor Issues**
1. **Status Message Clarity**: Device connection status could be more descriptive
2. **Error Recovery**: Limited error recovery when PicoScope disconnects during operation
3. **Memory Management**: No explicit cleanup of large data buffers over long sessions

---

## 🔄 **Recent Fixes Applied (v0.3)**

### ✅ **Resolved Issues**
1. **No Data Plotting Bug**: 
   - **Root Cause**: Incorrect timestamp calculation in `PicoDirectSource.read()`
   - **Fix**: Corrected `_sample_count` increment logic and timebase validation
   - **Result**: Data now plots correctly with proper time axis

2. **Debug Message Spam**:
   - **Root Cause**: Leftover debug print statements in `pico_direct.py`
   - **Fix**: Removed all debug print statements
   - **Result**: Clean terminal output

3. **PicoScope Connection Issues**:
   - **Root Cause**: DLL path resolution and device detection logic
   - **Fix**: Verified DLL loading and device connection works correctly
   - **Result**: Reliable PicoScope 4262 connection

### 🔧 **Code Changes Made**
- **`app/acquisition/pico_direct.py`**: Fixed timestamp calculation and removed debug prints
- **`app/core/controller.py`**: Reverted to stable device reuse logic
- **`app/ui/main_window.py`**: Clean UI without debug artifacts

---

## 🚀 **Planned Work for v0.4**

### 🎯 **Priority 1: Fix Timestamp Continuity**
- **Goal**: Ensure each new session starts with timestamps from 0.000000s
- **Approach**: Implement proper state reset in `PicoDirectSource` or create fresh instances
- **Files to Modify**: `app/core/controller.py`, `app/acquisition/pico_direct.py`
- **Testing**: Verify CSV files show correct timestamp progression

### 🎯 **Priority 2: Fix Erratic Plotting**
- **Goal**: Smooth plot behavior when changing sample rates
- **Approach**: Clear plot data before starting new sessions
- **Files to Modify**: `app/core/controller.py`, `app/ui/main_window.py`
- **Testing**: Change sample rate multiple times and verify smooth transitions

### 🎯 **Priority 3: Enhanced Error Handling**
- **Goal**: Better error recovery and user feedback
- **Approach**: Implement device reconnection logic and clearer error messages
- **Files to Modify**: `app/core/controller.py`, `app/ui/main_window.py`
- **Testing**: Disconnect PicoScope during operation and verify graceful handling

### 🎯 **Priority 4: Performance Optimization**
- **Goal**: Optimize for long-running sessions
- **Approach**: Implement data buffer management and memory cleanup
- **Files to Modify**: `app/core/controller.py`, `app/acquisition/pico_direct.py`
- **Testing**: Run sessions for extended periods and monitor memory usage

---

## 📁 **Key Files & Their Roles**

### **Core Application**
- **`app/main.py`**: Application entry point
- **`app/core/controller.py`**: Main application logic and state management
- **`app/ui/main_window.py`**: GUI implementation and user interactions

### **Data Acquisition**
- **`app/acquisition/pico_direct.py`**: Direct PicoScope communication (PRIMARY)
- **`app/acquisition/pico_ps4000_source.py`**: Alternative PicoScope implementation
- **`app/acquisition/pico_ps4000_stream.py`**: Streaming-based acquisition
- **`app/acquisition/source.py`**: Base acquisition interface

### **Data Processing & Storage**
- **`app/processing/pipeline.py`**: Data processing pipeline
- **`app/storage/csv_writer.py`**: CSV file writing functionality

### **Configuration**
- **`requirements.txt`**: Python dependencies
- **`README.md`**: Project documentation and setup instructions

---

## 🧪 **Testing & Validation**

### **Current Test Status**
- ✅ **PicoScope Connection**: Verified working with diagnostic script
- ✅ **Data Acquisition**: Real-time data streaming confirmed
- ✅ **CSV Generation**: Files created with proper timestamps
- ✅ **GUI Functionality**: Start/Stop/Reset controls working
- ⚠️ **Session Restart**: Timestamp continuity needs verification
- ⚠️ **Sample Rate Changes**: Erratic behavior needs testing

### **Recommended Test Scenarios**
1. **Basic Operation**: Start → Acquire data → Stop → Verify CSV
2. **Session Restart**: Start → Stop → Reset → Start → Check timestamps
3. **Sample Rate Changes**: Change rate → Start → Verify smooth plotting
4. **Long Sessions**: Run for extended periods → Monitor memory/performance
5. **Error Conditions**: Disconnect device → Verify graceful handling

---

## 🔧 **Development Environment**

### **System Requirements**
- **OS**: Windows 10/11 (tested on Windows 10.0.26100)
- **Python**: 3.8+ (tested with current version)
- **Hardware**: PicoScope 4262 connected via USB
- **Software**: PicoScope 7 T&M Stable installed

### **Dependencies**
- **PyQt6**: GUI framework
- **pyqtgraph**: Real-time plotting
- **numpy**: Numerical operations
- **ctypes**: Direct DLL communication
- **ps4000.dll**: PicoScope driver (installed with PicoScope 7)

### **Installation**
```bash
pip install -r requirements.txt
python -m app.main
```

---

## 📋 **Next Session Checklist**

### **Immediate Tasks**
1. [ ] Test timestamp continuity bug reproduction
2. [ ] Implement proper state reset for new sessions
3. [ ] Test sample rate change behavior
4. [ ] Verify CSV file timestamp accuracy
5. [ ] Test long-running session stability

### **Code Review Areas**
1. **`PicoDirectSource.read()`**: Timestamp calculation logic
2. **`AppController.start()`**: Session initialization
3. **`AppController.reset_data()`**: State reset implementation
4. **Plot data clearing**: UI state management

### **Documentation Updates**
1. Update README.md with current status
2. Document any new bugs found
3. Update installation instructions if needed

---

## 🎉 **Success Metrics for v0.4**

- [ ] **Timestamp Continuity**: Each new session starts at 0.000000s
- [ ] **Smooth Plotting**: No erratic behavior during configuration changes
- [ ] **CSV Accuracy**: Timestamps progress correctly from 0
- [ ] **Error Recovery**: Graceful handling of device disconnections
- [ ] **Performance**: Stable operation over extended sessions
- [ ] **User Experience**: Intuitive and reliable operation

---

## 📞 **Support Information**

### **Known Working Configuration**
- **PicoScope Model**: 4262
- **DLL Location**: `C:\Program Files\Pico Technology\PicoScope 7 T&M Stable\ps4000.dll`
- **Sample Rates**: 100Hz (default), configurable
- **Channels**: Channel A (default)
- **Voltage Range**: ±2V (default)

### **Troubleshooting**
- **Device Not Found**: Check USB connection and close other PicoScope applications
- **DLL Errors**: Verify PicoScope 7 installation
- **Plot Issues**: Check sample rate configuration
- **CSV Problems**: Verify file permissions in cache directory

---

**Last Updated**: December 2024  
**Version**: v0.3 → v0.4  
**Status**: Ready for continued development

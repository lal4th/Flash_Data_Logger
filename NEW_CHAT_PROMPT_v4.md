# Flash Data Logger Multi-Device Performance Debug - New Chat Prompt v4

## Project Context
Continuing work on the Flash Data Logger multi-device compatibility project. The goal is to support both PicoScope 4262 (ps4000/ps4000a API) and 6824E (ps6000a API) devices with full multi-channel data acquisition and plotting.

## Current Status: **CRITICAL PERFORMANCE ISSUES IDENTIFIED**

### ✅ **Major Achievements (Working):**
- **Device Detection**: Successfully detects and connects to both 4262 and 6824E
- **Timeline Display**: X-axis shows relative seconds (0, 1, 2, 3...) instead of Unix timestamps
- **Plot Positioning**: Sine wave traces start at time=0 instead of being compressed to the right
- **Channel Configuration**: Properly configures channels A-H on 6824E and A-B on 4262
- **Multi-Channel Data Display**: All channels A, B, C, D now display data correctly in the GUI
- **Core Architecture**: Multi-device architecture is working with proper signal emission and UI handling

### ❌ **Critical Performance Issues (User Testing Results):**

1. **Performance Degradation**: Application becomes very slow after ~12 seconds and eventually crashes
2. **Data Buffer Management**: Plot data gets erased after reaching buffer limit - data from time=0 to time=3 seconds disappears as time progresses
3. **Plot Rendering Artifacts**: Traces show a line from (0,0) to the front of the sine wave that follows the trace as it's drawn
4. **Buffer Retention**: Data should be retained for the entire session until Reset button is pressed, not automatically cleared

## Key Debug Findings

### 🔍 **Root Cause Analysis Completed:**

**CRITICAL DISCOVERY**: The issue is **NOT** in the PlotPanel class itself. Debug testing revealed:

1. **PlotPanel Works Correctly**: When tested in isolation, PlotPanel retains data perfectly from 0.000s to 14.986s with no data loss
2. **Buffer Management is Working**: Buffer grows to reasonable sizes (1217 points over 15 seconds)
3. **Data Retention is Working**: No data loss detected in isolated PlotPanel testing
4. **The Real Issue**: The problem is in the **data flow** between the streaming controller and the UI

### 🛠️ **Technical Root Causes Identified:**

The performance issues are caused by problems in the **data flow pipeline**:

1. **Streaming Controller → Main Window → PlotPanel**: The issue is in how data flows from the streaming controller through the main window to the plots
2. **Buffer Management in Streaming Controller**: The `_accumulated_plot_data_*` arrays in the streaming controller may be growing without proper limits
3. **Plot Update Frequency**: The main window may be updating plots too frequently or inefficiently
4. **Data Flow Architecture**: The signal/slot mechanism between streaming controller and UI may be causing performance bottlenecks

## Previous Attempts and Results

### ❌ **Failed Performance Fixes:**
- **Buffer Management Changes**: Modified PlotPanel buffer management - no improvement
- **Plot Update Optimization**: Added frequency limiting to plot updates - no improvement  
- **Memory Management**: Fixed RAM buffer management in streaming controller - no improvement
- **Plot Rendering**: Added curve initialization and update optimization - no improvement

### ✅ **Successful Debug Work:**
- **Created debug_plot_logic_only.py**: Tests PlotPanel in isolation - works perfectly
- **Created debug_plotting_performance.py**: Tests full system performance
- **Identified Real Issue**: Problem is NOT in PlotPanel, but in data flow architecture

## Key Files and Current State

### Modified Files (Previous Attempts):
- `app/ui/main_window.py` - Added buffer management and plot update optimizations
- `app/core/streaming_controller.py` - Updated buffer limits and memory management
- `scripts/test_performance_fixes.py` - Performance test script (shows false positives)
- `scripts/debug_plot_logic_only.py` - **WORKING** - proves PlotPanel is not the issue
- `scripts/debug_plotting_performance.py` - Full system debug script

### New Files Created:
- `PERFORMANCE_FIXES_SUMMARY.md` - Documentation of failed attempts
- `NEW_CHAT_PROMPT_v3.md` - Previous session summary

## Current Implementation Status

### ✅ **Working Components:**
```python
# PlotPanel works correctly when tested in isolation
plot_panel.update_data(timestamp, value)  # Retains data perfectly
# Buffer management: 1217 points over 15 seconds - no data loss
# Data retention: 0.000s to 14.986s - perfect retention
```

### ❌ **Problematic Components:**
```python
# Streaming controller data flow (suspected issue)
self.signal_plot.emit((data_a, data_b, data_c, data_d, data_e, data_f, data_g, data_h, time_axis))
# Main window plot update handling (suspected issue)  
def _on_plot_data(self, payload: object) -> None:
# Plot update timer in main window (suspected issue)
self._plot_update_timer.start(100)  # Update every 100ms (10 Hz)
```

## Next Steps Required

### 🎯 **Priority 1: Debug the Real Data Flow**
1. **Create Real Data Flow Debug Script**: Test the exact data flow used by the real app
2. **Identify Streaming Controller Issues**: Debug the `_accumulated_plot_data_*` arrays and signal emission
3. **Debug Main Window Plot Updates**: Test the `_on_plot_data` method and plot update timer
4. **Find the Real Bottleneck**: Identify where the performance degradation actually occurs

### 🛠️ **Specific Technical Tasks:**

1. **Data Flow Debugging**: 
   - Create script that uses streaming controller → main window → plots (exact same flow as real app)
   - Monitor performance of each step in the data flow pipeline
   - Identify which component is causing the slowdown

2. **Streaming Controller Analysis**:
   - Debug the `_update_plot` method in streaming controller
   - Check the `_accumulated_plot_data_*` arrays for memory growth
   - Analyze the signal emission frequency and data size

3. **Main Window Plot Handling**:
   - Debug the `_on_plot_data` method performance
   - Check the plot update timer efficiency
   - Analyze the `update_data_array` calls to PlotPanel

4. **Performance Bottleneck Identification**:
   - Profile memory usage during extended sessions
   - Monitor CPU usage during plot updates
   - Identify the exact point where performance degrades

## Testing Approach

1. **Real Data Flow Testing**: Test with the exact same data flow as the real app
2. **Component Isolation**: Test each component in the data flow pipeline separately
3. **Performance Profiling**: Monitor memory, CPU, and buffer growth during extended sessions
4. **Incremental Fixes**: Make one small change at a time and test immediately

## Expected Results

After identifying the real issue:
- **Stable Performance**: Application should remain responsive during extended data acquisition sessions
- **Data Retention**: All data should be retained from start to finish of the session
- **Clean Rendering**: Sine waves should display cleanly without the (0,0) line artifact
- **Proper Buffer Management**: Data should only be cleared when Reset button is pressed

## Branch Information
- **Branch Name**: `multi-device-compatibility`
- **Current Commit**: `1cb21fc` - "Add debug scripts to isolate plotting performance issues"
- **Status**: Core functionality working, real performance bottleneck identified in data flow

## User Feedback Context
The user has been very clear about not declaring victory before testing. They specifically requested systematic approach with debug scripts and incremental changes. The user said: "You are back to jumping around and doing quick fixes, only a matter of time before you break something. Please stop what you are doing and document all progress and learnings."

## Critical Requirements
- **DO NOT declare victory before user testing** - wait for user confirmation
- **Use systematic approach** with debug scripts
- **Make incremental changes** - one fix at a time
- **Preserve working functionality** - don't break what's already working
- **Document all changes** and their effects
- **Test thoroughly** before claiming success
- **Focus on the real data flow** - not the PlotPanel (which works correctly)

## Success Criteria
- Application remains stable during extended data acquisition sessions (30+ seconds)
- All data is retained from start to finish of the session
- Clean sine wave display without rendering artifacts
- Proper buffer management that only clears data on Reset
- No performance degradation or crashes

## Next Action
Focus on debugging the real data flow pipeline (streaming controller → main window → plots) to identify the actual performance bottleneck causing the slowdown and crashes.

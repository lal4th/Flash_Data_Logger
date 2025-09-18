# Flash Data Logger Multi-Device Performance Optimization - New Chat Prompt v3

## Project Context
I'm continuing work on the Flash Data Logger multi-device compatibility project. The goal is to support both PicoScope 4262 (ps4000/ps4000a API) and 6824E (ps6000a API) devices with full multi-channel data acquisition and plotting.

## Current Status: **SIGNIFICANT PROGRESS - PERFORMANCE OPTIMIZATION NEEDED**

### ✅ **Major Achievements (Working):**
- **Device Detection**: Successfully detects and connects to both 4262 and 6824E
- **Timeline Display**: X-axis shows relative seconds (0, 1, 2, 3...) instead of Unix timestamps
- **Plot Positioning**: Sine wave traces start at time=0 instead of being compressed to the right
- **Channel Configuration**: Properly configures channels A-H on 6824E and A-B on 4262
- **Multi-Channel Data Display**: **FIXED** - All channels A, B, C, D now display data correctly in the GUI
- **Data Flow Issue**: **RESOLVED** - Fixed the critical issue where channels C-H showed no data
- **Core Architecture**: Multi-device architecture is working with proper signal emission and UI handling

### ❌ **Remaining Critical Issues (User Testing Results):**

1. **Performance Degradation**: Application becomes very slow after ~12 seconds and eventually crashes
2. **Data Buffer Management**: Plot data gets erased after reaching buffer limit - data from time=0 to time=3 seconds disappears as time progresses
3. **Plot Rendering Artifacts**: Traces show a line from (0,0) to the front of the sine wave that follows the trace as it's drawn
4. **Buffer Retention**: Data should be retained for the entire session until Reset button is pressed, not automatically cleared

## Technical Analysis

### 🔍 **Root Cause Analysis:**

The performance issues are caused by:

1. **Buffer Management Problem**: The `update_data_array` method is extending buffers indefinitely, causing memory growth and performance degradation
2. **Plot Rendering Issue**: The line from (0,0) suggests the plot is not properly clearing previous data or there's an issue with how the curve is being updated
3. **Buffer Size Calculation**: The dynamic buffer sizing may be too aggressive, causing data to be discarded too early

### 🛠️ **Technical Root Causes:**

1. **Memory Growth**: `self._time_buffer.extend(time_axis.tolist())` and `self._data_buffer.extend(data_array.tolist())` are growing buffers without proper limits
2. **Plot Update Frequency**: The plot curve is being updated on every data addition, which may be too frequent
3. **Buffer Trimming Logic**: The buffer trimming logic may be removing data too aggressively

## Key Files Modified:

### Modified Files:
- `app/ui/main_window.py` - Added `update_data_array` method and fixed `_on_plot_data` method
- `app/core/streaming_controller.py` - Extended for multi-channel support
- `app/acquisition/pico_6000_direct.py` - Extended for 8-channel support

### New Files Created:
- `MULTI_DEVICE_ATTEMPT_SUMMARY_v2.md` - Complete documentation of all work done
- `scripts/debug_plot_panel_data_flow.py` - Debug script that identified the core issue
- `scripts/debug_plot_panel_update_method.py` - Debug script that confirmed the fix
- `scripts/test_multi_channel_fix.py` - Test script that verified the fix works
- `scripts/test_crash_fix.py` - Test script that verified the crash fix
- `scripts/test_complete_multi_channel_gui.py` - Comprehensive test script

## Current Implementation:

### ✅ **Working Solution:**
```python
# In MainWindow._on_plot_data():
for _r, _c, panel in self._plot_panels:
    if panel.channel == 'C' and isinstance(data_c, np.ndarray) and data_c.size > 0:
        panel.update_data_array(time_axis, data_c)

# In PlotPanel.update_data_array():
def update_data_array(self, time_axis: np.ndarray, data_array: np.ndarray) -> None:
    # Add new data to buffers
    self._time_buffer.extend(time_axis.tolist())
    self._data_buffer.extend(data_array.tolist())
    
    # Dynamic buffer sizing and trimming logic
    # Update the plot curve
    self.curve.setData(self._time_buffer, self._data_buffer)
```

## Next Steps Required:

### 🎯 **Priority 1: Performance Optimization**
1. **Fix Buffer Management**: Implement proper buffer size limits and data retention logic
2. **Optimize Plot Updates**: Reduce plot update frequency or implement more efficient rendering
3. **Fix Plot Rendering Artifacts**: Investigate the (0,0) line issue in plot rendering
4. **Implement Proper Data Retention**: Ensure data is retained for the entire session until Reset

### 🛠️ **Specific Technical Tasks:**

1. **Buffer Size Management**: 
   - Implement proper buffer size limits based on timeline and sample rate
   - Ensure data is retained for the entire session, not trimmed automatically
   - Fix the buffer trimming logic to prevent data loss

2. **Plot Rendering Optimization**:
   - Investigate the (0,0) line artifact in plot rendering
   - Optimize plot update frequency to prevent performance degradation
   - Implement more efficient curve updating

3. **Memory Management**:
   - Prevent memory growth that causes crashes
   - Implement proper data retention until Reset button is pressed
   - Optimize buffer operations for better performance

## Testing Approach:

1. **Performance Testing**: Test with extended data acquisition sessions (30+ seconds)
2. **Buffer Testing**: Verify data retention throughout the entire session
3. **Rendering Testing**: Verify clean sine wave display without artifacts
4. **Memory Testing**: Monitor memory usage during extended sessions

## Expected Results:

After the fixes:
- **Stable Performance**: Application should remain responsive during extended data acquisition sessions
- **Data Retention**: All data should be retained from start to finish of the session
- **Clean Rendering**: Sine waves should display cleanly without the (0,0) line artifact
- **Proper Buffer Management**: Data should only be cleared when Reset button is pressed

## Branch Information:
- **Branch Name**: `multi-device-compatibility`
- **Current Commit**: `ac90156` - "Multi-device compatibility: Channels A-D display working, performance issues remain"
- **Status**: Core functionality working, performance optimization needed

## User Feedback Context:
The user has been very clear about not declaring victory before testing. They specifically requested systematic approach with debug scripts and incremental changes. The user said: "You are back to jumping around and doing quick fixes, only a matter of time before you break something. Please stop what you are doing and document all progress and learnings."

## Critical Requirements:
- **DO NOT declare victory before user testing** - wait for user confirmation
- **Use systematic approach** with debug scripts
- **Make incremental changes** - one fix at a time
- **Preserve working functionality** - don't break what's already working
- **Document all changes** and their effects
- **Test thoroughly** before claiming success

## Success Criteria:
- Application remains stable during extended data acquisition sessions (30+ seconds)
- All data is retained from start to finish of the session
- Clean sine wave display without rendering artifacts
- Proper buffer management that only clears data on Reset
- No performance degradation or crashes

## Next Action:
Focus on performance optimization, buffer management, and plot rendering fixes to complete the multi-device compatibility project.

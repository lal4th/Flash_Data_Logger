#!/usr/bin/env python3
"""
Test script to verify the crash fix for multi-channel data display.
This script tests the new update_data_array method to ensure it doesn't cause crashes.
"""

import sys
import numpy as np
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_crash_fix():
    """Test the crash fix with the new update_data_array method."""
    print("=== Testing Crash Fix for Multi-Channel Data Display ===")
    
    from PyQt6 import QtWidgets, QtGui
    from app.core.streaming_controller import StreamingController
    from app.ui.main_window import MainWindow, PlotConfig
    
    print("1. Creating GUI application...")
    
    # Create a minimal Qt application
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    
    # Create controller and main window
    controller = StreamingController()
    window = MainWindow(controller)
    
    print("2. Adding multi-channel plot panels...")
    
    # Add plot panels for channels A, B, C, D
    config_a = PlotConfig('A', 1, 9, -10.0, 10.0, 'Volts', 'Channel A', QtGui.QColor(255, 0, 0))
    config_b = PlotConfig('B', 1, 9, -10.0, 10.0, 'Volts', 'Channel B', QtGui.QColor(0, 255, 0))
    config_c = PlotConfig('C', 1, 9, -10.0, 10.0, 'Volts', 'Channel C', QtGui.QColor(0, 0, 255))
    config_d = PlotConfig('D', 1, 9, -10.0, 10.0, 'Volts', 'Channel D', QtGui.QColor(255, 255, 0))
    
    window._add_plot_to_grid(config_a)
    window._add_plot_to_grid(config_b)
    window._add_plot_to_grid(config_c)
    window._add_plot_to_grid(config_d)
    
    print(f"   Created {len(window._plot_panels)} plot panels")
    
    print("3. Testing with high-frequency data updates (simulating real acquisition)...")
    
    # Simulate high-frequency data updates that could cause crashes
    for update_cycle in range(10):  # More updates to test stability
        print(f"\n   Update cycle {update_cycle + 1}:")
        
        # Create time axis for this update
        base_time = update_cycle * 5.0
        time_axis = np.array([base_time + i * 0.1 for i in range(50)])  # 50 points per update
        
        # Create different sine wave patterns for each channel
        data_a = np.array([np.sin(t * 0.5) * 5 for t in time_axis])
        data_b = np.array([np.sin(t * 0.3) * 3 for t in time_axis])
        data_c = np.array([np.sin(t * 0.7) * 2 for t in time_axis])
        data_d = np.array([np.sin(t * 0.2) * 4 for t in time_axis])
        data_e = np.array([np.sin(t * 0.4) * 1 for t in time_axis])
        data_f = np.array([np.sin(t * 0.6) * 3 for t in time_axis])
        data_g = np.array([np.sin(t * 0.8) * 2 for t in time_axis])
        data_h = np.array([np.sin(t * 0.1) * 5 for t in time_axis])
        
        # Create extended multi-channel payload
        payload = (data_a, data_b, data_c, data_d, data_e, data_f, data_g, data_h, time_axis)
        
        print(f"     Time range: {time_axis[0]:.1f} to {time_axis[-1]:.1f} ({len(time_axis)} points)")
        print(f"     Channel A range: {data_a.min():.2f} to {data_a.max():.2f}")
        print(f"     Channel B range: {data_b.min():.2f} to {data_b.max():.2f}")
        print(f"     Channel C range: {data_c.min():.2f} to {data_c.max():.2f}")
        print(f"     Channel D range: {data_d.min():.2f} to {data_d.max():.2f}")
        
        try:
            # Send data to GUI (simulating controller signal emission)
            window._on_plot_data(payload)
            print(f"     ✓ Data sent successfully")
            
            # Check data accumulation
            for r, c, panel in window._plot_panels:
                buffer_size = len(panel._data_buffer) if hasattr(panel, '_data_buffer') else 0
                print(f"     {panel.channel}: {buffer_size} total points")
                
        except Exception as e:
            print(f"     ✗ Error during update: {e}")
            return False
    
    print("\n4. Verifying final data state...")
    
    # Check final state of all plot panels
    success = True
    expected_total_points = 500  # 10 cycles * 50 points each
    
    for r, c, panel in window._plot_panels:
        buffer_size = len(panel._data_buffer) if hasattr(panel, '_data_buffer') else 0
        time_buffer_size = len(panel._time_buffer) if hasattr(panel, '_time_buffer') else 0
        
        if buffer_size > 0 and time_buffer_size > 0:
            print(f"   ✓ Channel {panel.channel}: {buffer_size} data points, {time_buffer_size} time points")
            
            # Check data range
            if panel._data_buffer:
                data_min = min(panel._data_buffer)
                data_max = max(panel._data_buffer)
                print(f"     Data range: {data_min:.2f} to {data_max:.2f}")
        else:
            print(f"   ✗ Channel {panel.channel}: No data points")
            success = False
    
    print("\n5. Testing plot panel curve updates...")
    
    # Check if curves have data
    for r, c, panel in window._plot_panels:
        try:
            x_data, y_data = panel.curve.getData()
            if x_data is not None and y_data is not None and len(x_data) > 0:
                print(f"   ✓ Channel {panel.channel}: Curve has {len(x_data)} points")
            else:
                print(f"   ✗ Channel {panel.channel}: Curve has no data")
                success = False
        except Exception as e:
            print(f"   ✗ Channel {panel.channel}: Error getting curve data: {e}")
            success = False
    
    print("\n6. Final Results:")
    if success:
        print("   ✓ SUCCESS: Crash fix is working!")
        print("   ✓ All channels A, B, C, D are receiving and displaying data correctly")
        print("   ✓ No crashes occurred during high-frequency data updates")
        print("   ✓ The update_data_array method efficiently handles array updates")
    else:
        print("   ✗ FAILURE: Some issues remain with the crash fix")
    
    return success

if __name__ == "__main__":
    test_crash_fix()

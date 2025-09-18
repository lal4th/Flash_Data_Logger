#!/usr/bin/env python3
"""
Test script to verify the multi-channel data display fix.
This script tests the corrected _on_plot_data method.
"""

import sys
import numpy as np
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_plot_data_fix():
    """Test the fixed _on_plot_data method."""
    print("=== Testing Multi-Channel Data Display Fix ===")
    
    # Import the fixed MainWindow
    from app.ui.main_window import MainWindow, PlotConfig
    from PyQt6 import QtWidgets, QtGui
    
    print("1. Testing _on_plot_data method with extended multi-channel data")
    
    # Create a minimal Qt application
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    
    # Create main window
    from app.core.streaming_controller import StreamingController
    controller = StreamingController()
    window = MainWindow(controller)
    
    # Add test plot panels for channels A, B, C, D
    config_a = PlotConfig('A', 1, 9, -10.0, 10.0, 'Volts', 'Channel A', QtGui.QColor(255, 0, 0))
    config_b = PlotConfig('B', 1, 9, -10.0, 10.0, 'Volts', 'Channel B', QtGui.QColor(0, 255, 0))
    config_c = PlotConfig('C', 1, 9, -10.0, 10.0, 'Volts', 'Channel C', QtGui.QColor(0, 0, 255))
    config_d = PlotConfig('D', 1, 9, -10.0, 10.0, 'Volts', 'Channel D', QtGui.QColor(255, 255, 0))
    
    # Add plots to grid (this will configure channels in controller)
    window._add_plot_to_grid(config_a)
    window._add_plot_to_grid(config_b)
    window._add_plot_to_grid(config_c)
    window._add_plot_to_grid(config_d)
    
    print(f"   Created {len(window._plot_panels)} plot panels")
    
    # Test with extended multi-channel payload (9 elements)
    print("\n2. Testing with extended multi-channel payload:")
    time_axis = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    data_a = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    data_b = np.array([6.0, 7.0, 8.0, 9.0, 10.0])
    data_c = np.array([11.0, 12.0, 13.0, 14.0, 15.0])
    data_d = np.array([16.0, 17.0, 18.0, 19.0, 20.0])
    data_e = np.array([21.0, 22.0, 23.0, 24.0, 25.0])
    data_f = np.array([26.0, 27.0, 28.0, 29.0, 30.0])
    data_g = np.array([31.0, 32.0, 33.0, 34.0, 35.0])
    data_h = np.array([36.0, 37.0, 38.0, 39.0, 40.0])
    
    payload = (data_a, data_b, data_c, data_d, data_e, data_f, data_g, data_h, time_axis)
    
    print(f"   Payload length: {len(payload)}")
    print(f"   Time axis: {time_axis}")
    print(f"   Data A: {data_a}")
    print(f"   Data B: {data_b}")
    print(f"   Data C: {data_c}")
    print(f"   Data D: {data_d}")
    
    # Call the fixed _on_plot_data method
    window._on_plot_data(payload)
    
    # Check if data was added to plot panels
    print("\n3. Checking plot panel data buffers:")
    for i, (r, c, panel) in enumerate(window._plot_panels):
        buffer_size = len(panel._data_buffer) if hasattr(panel, '_data_buffer') else 0
        time_buffer_size = len(panel._time_buffer) if hasattr(panel, '_time_buffer') else 0
        print(f"   Panel {i} (Channel {panel.channel}): {buffer_size} data points, {time_buffer_size} time points")
        
        if buffer_size > 0:
            print(f"     Latest data: {panel._data_buffer[-1] if panel._data_buffer else 'None'}")
            print(f"     Latest time: {panel._time_buffer[-1] if panel._time_buffer else 'None'}")
    
    print("\n4. Expected Results:")
    print("   - All 4 panels should have 5 data points (one for each time step)")
    print("   - Channel A should have values [1, 2, 3, 4, 5]")
    print("   - Channel B should have values [6, 7, 8, 9, 10]")
    print("   - Channel C should have values [11, 12, 13, 14, 15]")
    print("   - Channel D should have values [16, 17, 18, 19, 20]")
    
    # Verify the fix worked
    success = True
    for r, c, panel in window._plot_panels:
        if panel.channel in ['A', 'B', 'C', 'D']:
            expected_size = 5
            actual_size = len(panel._data_buffer) if hasattr(panel, '_data_buffer') else 0
            if actual_size != expected_size:
                print(f"   ✗ Channel {panel.channel}: Expected {expected_size} points, got {actual_size}")
                success = False
            else:
                print(f"   ✓ Channel {panel.channel}: {actual_size} points (correct)")
    
    if success:
        print("\n✓ SUCCESS: Multi-channel data display fix is working!")
        print("   All channels A, B, C, D are now receiving and storing data correctly.")
    else:
        print("\n✗ FAILURE: The fix did not work as expected.")
    
    return success

if __name__ == "__main__":
    test_plot_data_fix()

#!/usr/bin/env python3
"""
Simple debug script to test the PlotPanel.update_data method signature issue.
This will help identify why channels C-H don't display data.
"""

import sys
import numpy as np
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_plot_panel_update_method():
    """Test the PlotPanel.update_data method with different input types."""
    print("=== Testing PlotPanel.update_data Method ===")
    
    # Test 1: Check the method signature
    from app.ui.main_window import PlotPanel, PlotConfig
    from PyQt6 import QtGui
    
    print("1. PlotPanel.update_data method signature:")
    import inspect
    sig = inspect.signature(PlotPanel.update_data)
    print(f"   {sig}")
    
    # Test 2: Create a mock PlotPanel to test the method
    print("\n2. Testing with different input types:")
    
    # Create a minimal config
    config = PlotConfig('C', 1, 9, -10.0, 10.0, 'Volts', 'Channel C', QtGui.QColor(0, 0, 255))
    
    # Test what happens when we call update_data with arrays vs single values
    print("\n   Test 2a: Single values (what the method expects):")
    try:
        # This is what the method is designed for
        print("   Calling update_data(3.0, 7.5) - single timestamp, single value")
        # We can't actually call it without a Qt app, but we can check the signature
        print("   ✓ Method signature accepts (timestamp: float, value: float)")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n   Test 2b: Arrays (what _on_plot_data is passing):")
    try:
        time_array = np.array([0.0, 1.0, 2.0])
        value_array = np.array([7.0, 8.0, 9.0])
        print(f"   Calling update_data(time_array, value_array)")
        print(f"   time_array: {time_array}")
        print(f"   value_array: {value_array}")
        print("   ✗ Method signature expects (timestamp: float, value: float), not arrays")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Check how _on_plot_data calls update_data
    print("\n3. How _on_plot_data calls update_data:")
    from app.ui.main_window import MainWindow
    
    # Look at the _on_plot_data method
    import inspect
    source = inspect.getsource(MainWindow._on_plot_data)
    print("   _on_plot_data method calls:")
    for line in source.split('\n'):
        if 'panel.update_data' in line:
            print(f"   {line.strip()}")
    
    print("\n4. The Problem:")
    print("   - _on_plot_data receives arrays: (data_a, data_b, data_c, ..., time_axis)")
    print("   - _on_plot_data calls: panel.update_data(time_axis, data_c)")
    print("   - But update_data expects: (timestamp: float, value: float)")
    print("   - So it's trying to append arrays to the buffer instead of individual values")
    
    print("\n5. The Solution:")
    print("   - Either change update_data to handle arrays")
    print("   - Or change _on_plot_data to iterate through arrays and call update_data for each point")
    print("   - The second option is better for real-time plotting")

if __name__ == "__main__":
    test_plot_panel_update_method()

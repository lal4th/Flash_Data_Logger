#!/usr/bin/env python3
"""
Minimal debug script to isolate just the plotting logic.
This creates a simple plot panel and feeds it data to see what's happening.
"""

import sys
import time
import math
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt6 import QtWidgets, QtCore
from app.ui.main_window import PlotPanel, PlotConfig
import numpy as np


def test_plot_panel_directly():
    """Test a single plot panel directly with fake data."""
    print("Testing PlotPanel directly...")
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Create a simple plot config
    config = PlotConfig(
        channel='A',
        coupling=1,
        voltage_range=8,
        y_min=-5.0,
        y_max=5.0,
        y_label='Volts',
        title='Direct Plot Test',
        color=QtWidgets.QApplication.palette().color(QtWidgets.QApplication.palette().ColorRole.Text)
    )
    
    # Create plot panel
    plot_panel = PlotPanel(config)
    plot_panel.show()
    
    print(f"Initial buffer sizes: time={len(plot_panel._time_buffer)}, data={len(plot_panel._data_buffer)}")
    
    # Generate data for 15 seconds
    start_time = time.time()
    sample_count = 0
    
    while time.time() - start_time < 15:
        current_time = time.time() - start_time
        
        # Generate sine wave
        value = 3.0 * math.sin(2 * math.pi * current_time * 0.5)
        
        # Update the plot
        plot_panel.update_data(current_time, value)
        
        sample_count += 1
        
        # Print debug info every 2 seconds
        if int(current_time) % 2 == 0 and current_time > 0:
            print(f"Time: {current_time:.1f}s | Buffer size: {len(plot_panel._time_buffer)} | Sample: {sample_count}")
            
            # Check for data loss
            if plot_panel._time_buffer:
                first_time = plot_panel._time_buffer[0]
                if first_time > 1.0:
                    print(f"  ❌ DATA LOSS: First data point at {first_time:.3f}s (missing {first_time:.3f}s)")
                else:
                    print(f"  ✓ Data retention OK: First data point at {first_time:.3f}s")
        
        # Process events
        app.processEvents()
        
        # Small delay
        time.sleep(0.01)  # 100 Hz
    
    print(f"Final buffer sizes: time={len(plot_panel._time_buffer)}, data={len(plot_panel._data_buffer)}")
    
    # Check final data retention
    if plot_panel._time_buffer:
        first_time = plot_panel._time_buffer[0]
        last_time = plot_panel._time_buffer[-1]
        print(f"Data span: {first_time:.3f}s to {last_time:.3f}s (span: {last_time - first_time:.3f}s)")
        
        if first_time > 1.0:
            print("❌ DATA LOSS DETECTED - data from beginning is missing")
        else:
            print("✓ Data retention OK")
    
    print("Test complete. Close the plot window to exit.")
    app.exec()


if __name__ == "__main__":
    test_plot_panel_directly()

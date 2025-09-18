#!/usr/bin/env python3
"""
Debug script to test the exact data flow from signal emission to plot panel updates.
This script will help identify the issue with channels C-H not displaying data.
"""

import sys
import numpy as np
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
from app.core.streaming_controller import StreamingController
from app.ui.main_window import MainWindow, PlotPanel, PlotConfig

class DebugMainWindow(MainWindow):
    """Debug version of MainWindow with logging for plot data flow."""
    
    def __init__(self, controller=None, parent=None):
        super().__init__(controller, parent)
        self.debug_log = []
    
    @QtCore.pyqtSlot(object)
    def _on_plot_data(self, payload: object) -> None:
        """Debug version of _on_plot_data with detailed logging."""
        print(f"\n=== DEBUG: _on_plot_data called ===")
        print(f"Payload type: {type(payload)}")
        print(f"Payload length: {len(payload) if hasattr(payload, '__len__') else 'N/A'}")
        
        if isinstance(payload, tuple):
            print(f"Payload elements: {[type(x).__name__ for x in payload]}")
            if len(payload) >= 3:
                print(f"First element (data_a) type: {type(payload[0])}, size: {payload[0].size if hasattr(payload[0], 'size') else 'N/A'}")
                print(f"Second element (data_b) type: {type(payload[1])}, size: {payload[1].size if hasattr(payload[1], 'size') else 'N/A'}")
                if len(payload) >= 4:
                    print(f"Third element (data_c) type: {type(payload[2])}, size: {payload[2].size if hasattr(payload[2], 'size') else 'N/A'}")
                if len(payload) >= 5:
                    print(f"Fourth element (data_d) type: {type(payload[3])}, size: {payload[3].size if hasattr(payload[3], 'size') else 'N/A'}")
                if len(payload) >= 9:
                    print(f"Last element (time_axis) type: {type(payload[-1])}, size: {payload[-1].size if hasattr(payload[-1], 'size') else 'N/A'}")
        
        # Call the original method
        super()._on_plot_data(payload)
        
        # Log plot panel states after update
        print(f"Number of plot panels: {len(self._plot_panels)}")
        for i, (r, c, panel) in enumerate(self._plot_panels):
            print(f"  Panel {i}: Channel {panel.channel}, Data buffer size: {len(panel._data_buffer) if hasattr(panel, '_data_buffer') else 'N/A'}")
            if hasattr(panel, '_data_buffer') and panel._data_buffer:
                print(f"    Latest data point: {panel._data_buffer[-1] if panel._data_buffer else 'None'}")
        print("=== END DEBUG ===\n")

class DebugPlotPanel(PlotPanel):
    """Debug version of PlotPanel with logging for update_data calls."""
    
    def update_data(self, timestamp, value):
        """Debug version of update_data with detailed logging."""
        print(f"DEBUG: PlotPanel.update_data called for channel {self.channel}")
        print(f"  Timestamp type: {type(timestamp)}, Value type: {type(value)}")
        
        if hasattr(timestamp, '__len__') and hasattr(value, '__len__'):
            print(f"  Timestamp is array with {len(timestamp)} elements")
            print(f"  Value is array with {len(value)} elements")
            print(f"  First timestamp: {timestamp[0] if len(timestamp) > 0 else 'None'}")
            print(f"  First value: {value[0] if len(value) > 0 else 'None'}")
            print(f"  Last timestamp: {timestamp[-1] if len(timestamp) > 0 else 'None'}")
            print(f"  Last value: {value[-1] if len(value) > 0 else 'None'}")
        else:
            print(f"  Timestamp: {timestamp}")
            print(f"  Value: {value}")
        
        # Call the original method
        super().update_data(timestamp, value)
        
        print(f"  After update: buffer size = {len(self._data_buffer) if hasattr(self, '_data_buffer') else 'N/A'}")
        print("DEBUG: PlotPanel.update_data completed\n")

def test_plot_data_flow():
    """Test the plot data flow with debug logging."""
    print("=== Testing Plot Data Flow ===")
    
    # Create a minimal Qt application
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    
    # Create debug main window
    controller = StreamingController()
    window = DebugMainWindow(controller)
    
    # Override PlotPanel class in the window
    window._original_plot_panel_class = PlotPanel
    # Replace PlotPanel with DebugPlotPanel for this test
    import app.ui.main_window
    app.ui.main_window.PlotPanel = DebugPlotPanel
    
    # Add some test plot panels
    config_a = PlotConfig('A', 1, 9, -10.0, 10.0, 'Volts', 'Channel A', QtGui.QColor(255, 0, 0))
    config_b = PlotConfig('B', 1, 9, -10.0, 10.0, 'Volts', 'Channel B', QtGui.QColor(0, 255, 0))
    config_c = PlotConfig('C', 1, 9, -10.0, 10.0, 'Volts', 'Channel C', QtGui.QColor(0, 0, 255))
    config_d = PlotConfig('D', 1, 9, -10.0, 10.0, 'Volts', 'Channel D', QtGui.QColor(255, 255, 0))
    
    window._add_plot_to_grid(config_a)
    window._add_plot_to_grid(config_b)
    window._add_plot_to_grid(config_c)
    window._add_plot_to_grid(config_d)
    
    print(f"Created {len(window._plot_panels)} plot panels")
    
    # Test with different payload types
    print("\n=== Test 1: Extended multi-channel payload (9 elements) ===")
    time_axis = np.array([0.0, 1.0, 2.0])
    data_a = np.array([1.0, 2.0, 3.0])
    data_b = np.array([4.0, 5.0, 6.0])
    data_c = np.array([7.0, 8.0, 9.0])
    data_d = np.array([10.0, 11.0, 12.0])
    data_e = np.array([13.0, 14.0, 15.0])
    data_f = np.array([16.0, 17.0, 18.0])
    data_g = np.array([19.0, 20.0, 21.0])
    data_h = np.array([22.0, 23.0, 24.0])
    
    payload = (data_a, data_b, data_c, data_d, data_e, data_f, data_g, data_h, time_axis)
    window._on_plot_data(payload)
    
    print("\n=== Test 2: Dual-channel payload (3 elements) ===")
    payload2 = (data_a, data_b, time_axis)
    window._on_plot_data(payload2)
    
    print("\n=== Test 3: Single data point (not arrays) ===")
    # Test what happens if we call update_data with single values instead of arrays
    for r, c, panel in window._plot_panels:
        if panel.channel == 'C':
            print(f"Testing single value update for channel {panel.channel}")
            panel.update_data(3.0, 7.5)  # Single timestamp, single value
    
    print("\n=== Test completed ===")
    
    # Don't show the window, just test the data flow
    return window

if __name__ == "__main__":
    test_plot_data_flow()

#!/usr/bin/env python3
"""
Debug script to investigate both the coupling issue and multi-channel data display issue.
This script will help us understand:
1. Why coupling shows as AC (1) when DC (0) is selected
2. Why channels C-H are not displaying data despite being configured
"""

import sys
import os
import numpy as np
from unittest.mock import Mock, MagicMock

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.streaming_controller import StreamingController, StreamingConfig
from app.acquisition.pico_6000_direct import Pico6000DirectSource

def test_coupling_mapping():
    """Test the coupling value mapping"""
    print("=== Testing Coupling Value Mapping ===\n")
    
    # From the terminal output, we see:
    # DEBUG: configure_channel() called with channel=0, enabled=True, coupling=0, range_val=9
    # ✓ Channel 0 configured (enabled=True, coupling=0, range=9)
    # But the status shows coupling=1 (AC)
    
    print("Expected coupling values:")
    print("  0 = DC coupling")
    print("  1 = AC coupling")
    print()
    
    # Test the Pico6000DirectSource coupling handling
    source = Pico6000DirectSource()
    
    print("Testing configure_channel with different coupling values:")
    
    # Test DC coupling (should be 0)
    print("DC coupling test:")
    result = source.configure_channel(0, enabled=True, coupling=0, range_val=9)
    print(f"  Result: {result}")
    print()
    
    # Test AC coupling (should be 1) 
    print("AC coupling test:")
    result = source.configure_channel(1, enabled=True, coupling=1, range_val=9)
    print(f"  Result: {result}")
    print()

def test_multi_channel_data_flow():
    """Test the complete multi-channel data flow"""
    print("=== Testing Multi-Channel Data Flow ===\n")
    
    # Create a streaming controller with multi-channel config
    controller = StreamingController()
    
    # Create config with all channels enabled
    config = StreamingConfig()
    config.multi_channel_mode = True
    config.channel_c_enabled = True
    config.channel_d_enabled = True
    config.channel_e_enabled = True
    config.channel_f_enabled = True
    config.channel_g_enabled = True
    config.channel_h_enabled = True
    
    controller._config = config
    
    # Mock the signal
    controller.signal_plot = Mock()
    
    print("1. Testing _queue_plot_data with extended multi-channel data:")
    
    # Simulate extended multi-channel data (list of tuples, each with 10 elements: timestamp + 8 channels + math_results)
    extended_data = [
        (0.0, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 0.0),  # timestamp + 8 channels + math_results
        (1.0, 1.1, 1.6, 2.1, 2.6, 3.1, 3.6, 4.1, 4.6, 0.0),
        (2.0, 1.2, 1.7, 2.2, 2.7, 3.2, 3.7, 4.2, 4.7, 0.0)
    ]
    
    # Test _queue_plot_data
    controller._queue_plot_data(extended_data)
    
    print(f"  Plot queue size: {controller._plot_queue.qsize()}")
    # Get queue content for inspection
    queue_content = []
    while not controller._plot_queue.empty():
        item = controller._plot_queue.get()
        queue_content.append(item)
    print(f"  Plot queue content: {len(queue_content)} items")
    
    # Put items back for further testing
    for item in queue_content:
        controller._plot_queue.put(item)
    print()
    
    print("2. Testing _update_plot signal emission:")
    
    # Clear any existing accumulated data
    controller._accumulated_plot_data_a = []
    controller._accumulated_plot_data_b = []
    controller._accumulated_plot_data_c = []
    controller._accumulated_plot_data_d = []
    controller._accumulated_plot_data_e = []
    controller._accumulated_plot_data_f = []
    controller._accumulated_plot_data_g = []
    controller._accumulated_plot_data_h = []
    controller._accumulated_plot_timestamps = []
    
    # Process the plot queue
    while not controller._plot_queue.empty():
        plot_data = controller._plot_queue.get()
        if len(plot_data) == 9:  # Extended multi-channel data: (data_a, data_b, data_c, data_d, data_e, data_f, data_g, data_h, timestamps)
            data_a, data_b, data_c, data_d, data_e, data_f, data_g, data_h, timestamps = plot_data
            # Extend the accumulated data arrays
            controller._accumulated_plot_data_a.extend(data_a)
            controller._accumulated_plot_data_b.extend(data_b)
            controller._accumulated_plot_data_c.extend(data_c)
            controller._accumulated_plot_data_d.extend(data_d)
            controller._accumulated_plot_data_e.extend(data_e)
            controller._accumulated_plot_data_f.extend(data_f)
            controller._accumulated_plot_data_g.extend(data_g)
            controller._accumulated_plot_data_h.extend(data_h)
            controller._accumulated_plot_timestamps.extend(timestamps)
    
    print(f"  Accumulated data lengths:")
    print(f"    A: {len(controller._accumulated_plot_data_a)}")
    print(f"    B: {len(controller._accumulated_plot_data_b)}")
    print(f"    C: {len(controller._accumulated_plot_data_c)}")
    print(f"    D: {len(controller._accumulated_plot_data_d)}")
    print(f"    E: {len(controller._accumulated_plot_data_e)}")
    print(f"    F: {len(controller._accumulated_plot_data_f)}")
    print(f"    G: {len(controller._accumulated_plot_data_g)}")
    print(f"    H: {len(controller._accumulated_plot_data_h)}")
    print(f"    Timestamps: {len(controller._accumulated_plot_timestamps)}")
    
    # Test the signal emission condition
    all_channel_c_values = all([
        len(controller._accumulated_plot_data_c) > 0,
        len(controller._accumulated_plot_data_d) > 0,
        len(controller._accumulated_plot_data_e) > 0,
        len(controller._accumulated_plot_data_f) > 0,
        len(controller._accumulated_plot_data_g) > 0,
        len(controller._accumulated_plot_data_h) > 0
    ])
    
    print(f"  all_channel_c_values: {all_channel_c_values}")
    
    # Test the current condition (after our fix)
    current_condition = all_channel_c_values
    print(f"  Current condition (after fix): {current_condition}")
    
    if current_condition:
        print("  ✓ Signal emission condition should pass")
        print("  ✓ Extended multi-channel data should be emitted")
    else:
        print("  ✗ Signal emission condition fails")
        print("  ✗ Extended multi-channel data will not be emitted")
    
    print()
    
    print("3. Testing actual signal emission:")
    
    # Simulate the _update_plot method logic
    if current_condition:
        # Convert to numpy arrays
        data_a = np.array(controller._accumulated_plot_data_a, dtype=float)
        data_b = np.array(controller._accumulated_plot_data_b, dtype=float)
        data_c = np.array(controller._accumulated_plot_data_c, dtype=float)
        data_d = np.array(controller._accumulated_plot_data_d, dtype=float)
        data_e = np.array(controller._accumulated_plot_data_e, dtype=float)
        data_f = np.array(controller._accumulated_plot_data_f, dtype=float)
        data_g = np.array(controller._accumulated_plot_data_g, dtype=float)
        data_h = np.array(controller._accumulated_plot_data_h, dtype=float)
        time_axis = np.array(controller._accumulated_plot_timestamps, dtype=float)
        
        # Emit extended multi-channel plot data
        controller.signal_plot.emit((data_a, data_b, data_c, data_d, data_e, data_f, data_g, data_h, time_axis))
        
        print("  ✓ Extended multi-channel signal emitted")
        print(f"  ✓ Signal called with {len(controller.signal_plot.emit.call_args[0][0])} elements")
        print(f"  ✓ Signal payload: {[len(arr) for arr in controller.signal_plot.emit.call_args[0][0]]}")
    else:
        print("  ✗ No signal emitted due to failed condition")
    
    print()

def test_ui_signal_handling():
    """Test how the UI handles the emitted signals"""
    print("=== Testing UI Signal Handling ===\n")
    
    # This would test the MainWindow._on_plot_data method
    # But we need to check if it's properly handling 9-element payloads
    
    print("UI should handle 9-element payloads for extended multi-channel data:")
    print("  Expected payload: (data_a, data_b, data_c, data_d, data_e, data_f, data_g, data_h, time_axis)")
    print("  Each data array should contain the channel values")
    print("  time_axis should contain the timestamps")
    print()
    
    # Check if the UI is properly configured to handle extended data
    print("Key questions to investigate:")
    print("  1. Is MainWindow._on_plot_data handling 9-element payloads?")
    print("  2. Are the plot widgets properly configured for channels C-H?")
    print("  3. Is the signal connection working properly?")
    print()

if __name__ == "__main__":
    test_coupling_mapping()
    test_multi_channel_data_flow()
    test_ui_signal_handling()

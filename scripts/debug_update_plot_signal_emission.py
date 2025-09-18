#!/usr/bin/env python3
"""
Debug script to test the _update_plot() method signal emission logic in isolation.
This script will help us understand why channels C-H are not emitting data to the UI.
"""

import sys
import os
import numpy as np
from unittest.mock import Mock, MagicMock

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.streaming_controller import StreamingController, StreamingConfig

def test_update_plot_signal_emission():
    """Test the _update_plot() method signal emission logic"""
    
    print("=== Testing _update_plot() Signal Emission Logic ===\n")
    
    # Create a mock streaming controller
    controller = StreamingController()
    
    # Create a mock config with multi-channel enabled
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
    
    # Test Case 1: First run - no accumulated data exists yet
    print("Test Case 1: First run - no accumulated data exists")
    print("-" * 50)
    
    # Simulate the condition from line 1177
    all_channel_c_values = True  # We have data for channels C-H
    
    # Check if the problematic condition would pass
    has_attr_c = hasattr(controller, '_accumulated_plot_data_c')
    print(f"hasattr(controller, '_accumulated_plot_data_c'): {has_attr_c}")
    
    if has_attr_c:
        len_c = len(controller._accumulated_plot_data_c)
        print(f"len(controller._accumulated_plot_data_c): {len_c}")
    else:
        print("_accumulated_plot_data_c does not exist")
    
    # Test the current condition
    current_condition = all_channel_c_values and hasattr(controller, '_accumulated_plot_data_c') and len(controller._accumulated_plot_data_c) > 0
    print(f"Current condition result: {current_condition}")
    
    # Test the proposed simplified condition
    simplified_condition = all_channel_c_values
    print(f"Simplified condition result: {simplified_condition}")
    
    print()
    
    # Test Case 2: After some data has been accumulated
    print("Test Case 2: After data accumulation")
    print("-" * 50)
    
    # Simulate accumulated data
    controller._accumulated_plot_data_a = [1.0, 2.0, 3.0]
    controller._accumulated_plot_data_b = [1.5, 2.5, 3.5]
    controller._accumulated_plot_data_c = [2.0, 3.0, 4.0]
    controller._accumulated_plot_data_d = [2.5, 3.5, 4.5]
    controller._accumulated_plot_data_e = [3.0, 4.0, 5.0]
    controller._accumulated_plot_data_f = [3.5, 4.5, 5.5]
    controller._accumulated_plot_data_g = [4.0, 5.0, 6.0]
    controller._accumulated_plot_data_h = [4.5, 5.5, 6.5]
    controller._accumulated_plot_timestamps = [0.0, 1.0, 2.0]
    
    # Check the condition again
    has_attr_c = hasattr(controller, '_accumulated_plot_data_c')
    print(f"hasattr(controller, '_accumulated_plot_data_c'): {has_attr_c}")
    
    if has_attr_c:
        len_c = len(controller._accumulated_plot_data_c)
        print(f"len(controller._accumulated_plot_data_c): {len_c}")
    
    current_condition = all_channel_c_values and hasattr(controller, '_accumulated_plot_data_c') and len(controller._accumulated_plot_data_c) > 0
    print(f"Current condition result: {current_condition}")
    
    simplified_condition = all_channel_c_values
    print(f"Simplified condition result: {simplified_condition}")
    
    print()
    
    # Test Case 3: Test the actual _update_plot method logic
    print("Test Case 3: Testing actual _update_plot method logic")
    print("-" * 50)
    
    # Mock the plot queue with extended data
    controller._plot_queue = [
        (0.0, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5),  # timestamp + 8 channels
        (1.0, 1.1, 1.6, 2.1, 2.6, 3.1, 3.6, 4.1, 4.6),
        (2.0, 1.2, 1.7, 2.2, 2.7, 3.2, 3.7, 4.2, 4.7)
    ]
    
    # Clear accumulated data to simulate first run
    controller._accumulated_plot_data_a = []
    controller._accumulated_plot_data_b = []
    controller._accumulated_plot_data_c = []
    controller._accumulated_plot_data_d = []
    controller._accumulated_plot_data_e = []
    controller._accumulated_plot_data_f = []
    controller._accumulated_plot_data_g = []
    controller._accumulated_plot_data_h = []
    controller._accumulated_plot_timestamps = []
    
    # Simulate the _update_plot method logic
    print("Simulating _update_plot method...")
    
    # Process plot queue
    for plot_data in controller._plot_queue:
        if len(plot_data) == 9:  # Extended multi-channel data
            timestamp, data_a, data_b, data_c, data_d, data_e, data_f, data_g, data_h = plot_data
            controller._accumulated_plot_data_a.append(data_a)
            controller._accumulated_plot_data_b.append(data_b)
            controller._accumulated_plot_data_c.append(data_c)
            controller._accumulated_plot_data_d.append(data_d)
            controller._accumulated_plot_data_e.append(data_e)
            controller._accumulated_plot_data_f.append(data_f)
            controller._accumulated_plot_data_g.append(data_g)
            controller._accumulated_plot_data_h.append(data_h)
            controller._accumulated_plot_timestamps.append(timestamp)
    
    print(f"Accumulated data lengths:")
    print(f"  A: {len(controller._accumulated_plot_data_a)}")
    print(f"  B: {len(controller._accumulated_plot_data_b)}")
    print(f"  C: {len(controller._accumulated_plot_data_c)}")
    print(f"  D: {len(controller._accumulated_plot_data_d)}")
    print(f"  E: {len(controller._accumulated_plot_data_e)}")
    print(f"  F: {len(controller._accumulated_plot_data_f)}")
    print(f"  G: {len(controller._accumulated_plot_data_g)}")
    print(f"  H: {len(controller._accumulated_plot_data_h)}")
    print(f"  Timestamps: {len(controller._accumulated_plot_timestamps)}")
    
    # Test the signal emission condition
    all_channel_c_values = all([
        len(controller._accumulated_plot_data_c) > 0,
        len(controller._accumulated_plot_data_d) > 0,
        len(controller._accumulated_plot_data_e) > 0,
        len(controller._accumulated_plot_data_f) > 0,
        len(controller._accumulated_plot_data_g) > 0,
        len(controller._accumulated_plot_data_h) > 0
    ])
    
    print(f"\nall_channel_c_values: {all_channel_c_values}")
    
    # Test current condition
    current_condition = all_channel_c_values and hasattr(controller, '_accumulated_plot_data_c') and len(controller._accumulated_plot_data_c) > 0
    print(f"Current condition: {current_condition}")
    
    # Test simplified condition
    simplified_condition = all_channel_c_values
    print(f"Simplified condition: {simplified_condition}")
    
    print("\n=== Analysis ===")
    print("The current condition fails on first run because:")
    print("1. _accumulated_plot_data_c doesn't exist initially (hasattr fails)")
    print("2. Even when it exists, the length check is redundant since all_channel_c_values already checks this")
    print("3. The simplified condition should work: if all_channel_c_values:")
    
    return current_condition, simplified_condition

if __name__ == "__main__":
    test_update_plot_signal_emission()

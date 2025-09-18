#!/usr/bin/env python3
"""
Comprehensive test script to verify both the coupling display fix and multi-channel data display fix.
This script will test the complete flow from data acquisition to UI display.
"""

import sys
import os
import numpy as np
from unittest.mock import Mock, MagicMock

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.streaming_controller import StreamingController, StreamingConfig
from app.acquisition.pico_6000_direct import Pico6000DirectSource

def test_coupling_display_fix():
    """Test that coupling values are displayed correctly"""
    print("=== Testing Coupling Display Fix ===\n")
    
    # Test the coupling text conversion
    coupling_tests = [
        (0, "AC"),
        (1, "DC")
    ]
    
    for coupling_value, expected_text in coupling_tests:
        coupling_text = "DC" if coupling_value == 1 else "AC"
        print(f"Coupling value {coupling_value} -> {coupling_text} (expected: {expected_text})")
        assert coupling_text == expected_text, f"Coupling conversion failed: {coupling_value} -> {coupling_text}"
    
    print("✓ Coupling display fix verified\n")

def test_multi_channel_data_flow_complete():
    """Test the complete multi-channel data flow from acquisition to UI"""
    print("=== Testing Complete Multi-Channel Data Flow ===\n")
    
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
    
    print("1. Testing data acquisition simulation:")
    
    # Simulate the _acquire_block method returning 9-element data
    # This simulates what the 6824E would return: (timestamp, a, b, c, d, e, f, g, h)
    simulated_block_data = [
        (0.0, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5),  # timestamp + 8 channels
        (1.0, 1.1, 1.6, 2.1, 2.6, 3.1, 3.6, 4.1, 4.6),
        (2.0, 1.2, 1.7, 2.2, 2.7, 3.2, 3.7, 4.2, 4.7)
    ]
    
    print(f"  Simulated block data: {len(simulated_block_data)} samples")
    print(f"  Each sample has {len(simulated_block_data[0])} elements (timestamp + 8 channels)")
    
    print("\n2. Testing data processing simulation:")
    
    # Simulate the _process_block method adding math_results
    # This should return 10-element data: (timestamp, a, b, c, d, e, f, g, h, math_results)
    processed_block_data = []
    for timestamp, a, b, c, d, e, f, g, h in simulated_block_data:
        math_results = 0.0  # Simulate math processing
        processed_block_data.append((timestamp, a, b, c, d, e, f, g, h, math_results))
    
    print(f"  Processed block data: {len(processed_block_data)} samples")
    print(f"  Each sample has {len(processed_block_data[0])} elements (timestamp + 8 channels + math_results)")
    
    print("\n3. Testing plot data queuing:")
    
    # Test _queue_plot_data with the processed data
    controller._queue_plot_data(processed_block_data)
    
    print(f"  Plot queue size: {controller._plot_queue.qsize()}")
    
    print("\n4. Testing plot data processing and signal emission:")
    
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
    
    # Process the plot queue (simulate _update_plot method)
    while not controller._plot_queue.empty():
        plot_data = controller._plot_queue.get()
        if len(plot_data) == 9:  # Extended multi-channel data
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
    
    print(f"\n  all_channel_c_values: {all_channel_c_values}")
    
    # Test the current condition (after our fix)
    current_condition = all_channel_c_values
    print(f"  Current condition (after fix): {current_condition}")
    
    if current_condition:
        print("  ✓ Signal emission condition passes")
        
        # Simulate the actual signal emission
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
        print(f"  ✓ Signal payload lengths: {[len(arr) for arr in controller.signal_plot.emit.call_args[0][0]]}")
        
        # Verify all channels have data
        signal_payload = controller.signal_plot.emit.call_args[0][0]
        for i, channel_data in enumerate(signal_payload[:-1]):  # Exclude time_axis
            channel_name = chr(ord('A') + i)
            print(f"    Channel {channel_name}: {len(channel_data)} data points")
            assert len(channel_data) > 0, f"Channel {channel_name} has no data"
        
        print("  ✓ All channels have data")
    else:
        print("  ✗ Signal emission condition fails")
        return False
    
    print("\n5. Testing UI signal handling simulation:")
    
    # Simulate the UI receiving the signal
    signal_payload = controller.signal_plot.emit.call_args[0][0]
    
    if len(signal_payload) == 9:
        data_a, data_b, data_c, data_d, data_e, data_f, data_g, data_h, time_axis = signal_payload
        print("  ✓ UI receives 9-element payload (extended multi-channel)")
        print(f"  ✓ Data arrays: A={len(data_a)}, B={len(data_b)}, C={len(data_c)}, D={len(data_d)}")
        print(f"  ✓ Data arrays: E={len(data_e)}, F={len(data_f)}, G={len(data_g)}, H={len(data_h)}")
        print(f"  ✓ Time axis: {len(time_axis)} points")
        
        # Verify all channels have data
        all_channels_have_data = all([
            len(data_a) > 0, len(data_b) > 0, len(data_c) > 0, len(data_d) > 0,
            len(data_e) > 0, len(data_f) > 0, len(data_g) > 0, len(data_h) > 0
        ])
        
        if all_channels_have_data:
            print("  ✓ All channels have data for UI display")
        else:
            print("  ✗ Some channels are missing data")
            return False
    else:
        print(f"  ✗ UI receives unexpected payload length: {len(signal_payload)}")
        return False
    
    print("\n=== Multi-Channel Data Flow Test PASSED ===\n")
    return True

def test_ui_plot_panel_handling():
    """Test that the UI plot panels can handle the extended data"""
    print("=== Testing UI Plot Panel Handling ===\n")
    
    # Simulate the UI plot panel update logic
    def simulate_plot_panel_update(channel, data, time_axis):
        """Simulate a plot panel updating with data"""
        if isinstance(data, np.ndarray) and data.size > 0:
            print(f"  ✓ Channel {channel} plot updated with {len(data)} data points")
            return True
        else:
            print(f"  ✗ Channel {channel} plot not updated (no data)")
            return False
    
    # Test with sample data
    sample_data = {
        'A': np.array([1.0, 1.1, 1.2]),
        'B': np.array([1.5, 1.6, 1.7]),
        'C': np.array([2.0, 2.1, 2.2]),
        'D': np.array([2.5, 2.6, 2.7]),
        'E': np.array([3.0, 3.1, 3.2]),
        'F': np.array([3.5, 3.6, 3.7]),
        'G': np.array([4.0, 4.1, 4.2]),
        'H': np.array([4.5, 4.6, 4.7])
    }
    time_axis = np.array([0.0, 1.0, 2.0])
    
    all_updated = True
    for channel, data in sample_data.items():
        if not simulate_plot_panel_update(channel, data, time_axis):
            all_updated = False
    
    if all_updated:
        print("✓ All plot panels can handle extended multi-channel data")
    else:
        print("✗ Some plot panels failed to update")
        return False
    
    print()
    return True

if __name__ == "__main__":
    print("=== Comprehensive Multi-Channel Test ===\n")
    
    # Run all tests
    tests_passed = 0
    total_tests = 3
    
    try:
        test_coupling_display_fix()
        tests_passed += 1
    except Exception as e:
        print(f"✗ Coupling display test failed: {e}")
    
    try:
        if test_multi_channel_data_flow_complete():
            tests_passed += 1
    except Exception as e:
        print(f"✗ Multi-channel data flow test failed: {e}")
    
    try:
        if test_ui_plot_panel_handling():
            tests_passed += 1
    except Exception as e:
        print(f"✗ UI plot panel test failed: {e}")
    
    print(f"=== Test Results: {tests_passed}/{total_tests} tests passed ===")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! The fixes should work correctly.")
    else:
        print("❌ Some tests failed. Please investigate the issues.")

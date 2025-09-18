#!/usr/bin/env python3
"""
Debug the actual GUI execution context to see what's happening during real-time execution.
"""

from __future__ import annotations

import sys
import time
import numpy as np
from PyQt6 import QtWidgets, QtCore

# Add the app directory to the path
sys.path.insert(0, '.')

from app.core.streaming_controller import StreamingController
from app.ui.main_window import MainWindow


def main() -> int:
    print("\n=== GUI Execution Context Debug ===")
    
    # Create Qt application
    app = QtWidgets.QApplication(sys.argv)
    
    # Create controller and main window
    controller = StreamingController()
    main_window = MainWindow(controller)
    
    # Enable channels A, B, C, and D
    print("Enabling channels A, B, C, and D...")
    controller.set_channel_a_config(True, 1, 8)
    controller.set_channel_b_config(True, 1, 8)
    controller.set_channel_c_config(True, 1, 8)
    controller.set_channel_d_config(True, 1, 8)
    
    # Test the controller setup
    print("\nTesting controller setup...")
    controller.probe_device()
    
    if controller._pico_6000_source:
        print("✓ 6824E connected")
        
        # Test the _setup_data_source method
        print("\nTesting _setup_data_source...")
        try:
            source_msg = controller._setup_data_source()
            print(f"  ✓ _setup_data_source succeeded: {source_msg}")
        except Exception as e:
            print(f"  ✗ _setup_data_source failed: {e}")
            return 1
        
        # Test the real-time execution flow
        print("\nTesting real-time execution flow...")
        try:
            # Start the controller (like the GUI would do)
            print("  Starting controller...")
            controller.start()
            print("  ✓ Controller started")
            
            # Wait a bit for data to accumulate
            print("  Waiting for data accumulation...")
            time.sleep(2.0)
            
            # Check if data is being acquired
            print("  Checking data acquisition...")
            if hasattr(controller, '_samples_acquired'):
                print(f"    Samples acquired: {controller._samples_acquired}")
            if hasattr(controller, '_samples_processed'):
                print(f"    Samples processed: {controller._samples_processed}")
            
            # Check plot queue contents
            print("  Checking plot queue...")
            plot_queue_size = controller._plot_queue.qsize()
            print(f"    Plot queue size: {plot_queue_size}")
            
            if plot_queue_size > 0:
                # Get a sample from the plot queue
                plot_payload = controller._plot_queue.get_nowait()
                print(f"    Plot payload: {len(plot_payload)} elements")
                print(f"    Payload types: {[type(x).__name__ for x in plot_payload]}")
                print(f"    Payload shapes: {[x.shape if hasattr(x, 'shape') else len(x) for x in plot_payload]}")
                
                # Check if channels C and D have data
                if len(plot_payload) == 9:  # Extended multi-channel
                    data_c, data_d = plot_payload[2], plot_payload[3]
                    print(f"    Channel C data: {data_c[:3]}... (length: {len(data_c)})")
                    print(f"    Channel D data: {data_d[:3]}... (length: {len(data_d)})")
                    
                    # Check if data is non-zero
                    c_nonzero = any(abs(x) > 1e-6 for x in data_c)
                    d_nonzero = any(abs(x) > 1e-6 for x in data_d)
                    print(f"    Channel C has non-zero data: {c_nonzero}")
                    print(f"    Channel D has non-zero data: {d_nonzero}")
                else:
                    print(f"    ❌ Expected 9 elements, got {len(plot_payload)}")
            else:
                print("    ❌ Plot queue is empty")
            
            # Stop the controller
            print("  Stopping controller...")
            controller.stop()
            print("  ✓ Controller stopped")
            
        except Exception as e:
            print(f"  ✗ Real-time execution flow failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
    else:
        print("✗ 6824E not connected")
        return 1
    
    print("\n✓ GUI execution context debug completed!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


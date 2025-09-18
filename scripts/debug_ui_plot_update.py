#!/usr/bin/env python3
"""
Debug the UI plot update to see if the issue is in the UI's _on_plot_data method.
"""

from __future__ import annotations

import sys
import numpy as np
from PyQt6 import QtWidgets, QtCore

# Add the app directory to the path
sys.path.insert(0, '.')

from app.core.streaming_controller import StreamingController
from app.ui.main_window import MainWindow


def main() -> int:
    print("\n=== UI Plot Update Debug ===")
    
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
        
        # Test the complete flow: acquire -> process -> queue -> update
        print("\nTesting complete plot update flow...")
        try:
            # Step 1: Acquire data
            block_data = controller._acquire_block()
            print(f"  ✓ _acquire_block: {len(block_data)} samples, {len(block_data[0])} elements per sample")
            
            # Step 2: Process data
            processed_data = controller._process_block(block_data)
            print(f"  ✓ _process_block: {len(processed_data)} samples, {len(processed_data[0])} elements per sample")
            
            # Step 3: Queue plot data
            controller._queue_plot_data(processed_data)
            print(f"  ✓ _queue_plot_data: succeeded")
            
            # Step 4: Get plot payload
            if not controller._plot_queue.empty():
                plot_payload = controller._plot_queue.get_nowait()
                print(f"  ✓ Plot queue: {len(plot_payload)} elements")
                
                # Step 5: Test UI plot update
                print("\nTesting UI plot update...")
                try:
                    # Create some mock plot panels for testing
                    print("  Creating mock plot panels...")
                    
                    # Test the _on_plot_data method directly
                    print("  Testing _on_plot_data method...")
                    main_window._on_plot_data(plot_payload)
                    print("  ✓ _on_plot_data succeeded")
                    
                except Exception as e:
                    print(f"  ✗ UI plot update failed: {e}")
                    import traceback
                    traceback.print_exc()
                    return 1
            
        except Exception as e:
            print(f"  ✗ Complete plot update flow failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
    else:
        print("✗ 6824E not connected")
        return 1
    
    print("\n✓ UI plot update debug completed!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


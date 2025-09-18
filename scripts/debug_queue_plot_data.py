#!/usr/bin/env python3
"""
Debug the _queue_plot_data method to identify the variable conflict.
"""

from __future__ import annotations

from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== _queue_plot_data Method Debug ===")
    
    c = StreamingController()
    
    # Enable channels A, B, C, and D
    print("Enabling channels A, B, C, and D...")
    c.set_channel_a_config(True, 1, 8)
    c.set_channel_b_config(True, 1, 8)
    c.set_channel_c_config(True, 1, 8)
    c.set_channel_d_config(True, 1, 8)
    
    # Test the controller setup
    print("\nTesting controller setup...")
    c.probe_device()
    
    if c._pico_6000_source:
        print("✓ 6824E connected")
        
        # Test the _setup_data_source method
        print("\nTesting _setup_data_source...")
        try:
            source_msg = c._setup_data_source()
            print(f"  ✓ _setup_data_source succeeded: {source_msg}")
        except Exception as e:
            print(f"  ✗ _setup_data_source failed: {e}")
            return 1
        
        # Test the _acquire_block method
        print("\nTesting _acquire_block...")
        try:
            block_data = c._acquire_block()
            print(f"  ✓ _acquire_block succeeded: {len(block_data)} samples")
        except Exception as e:
            print(f"  ✗ _acquire_block failed: {e}")
            return 1
        
        # Test the _process_block method
        print("\nTesting _process_block...")
        try:
            processed_data = c._process_block(block_data)
            print(f"  ✓ _process_block succeeded: {len(processed_data)} samples")
        except Exception as e:
            print(f"  ✗ _process_block failed: {e}")
            return 1
        
        # Debug the _queue_plot_data method step by step
        print("\nDebugging _queue_plot_data method...")
        try:
            # Check the method exists
            print(f"  _queue_plot_data method exists: {hasattr(c, '_queue_plot_data')}")
            print(f"  _queue_plot_data method type: {type(getattr(c, '_queue_plot_data', None))}")
            
            # Check processed_data structure
            print(f"  processed_data type: {type(processed_data)}")
            print(f"  processed_data length: {len(processed_data)}")
            if processed_data:
                print(f"  processed_data[0] type: {type(processed_data[0])}")
                print(f"  processed_data[0] length: {len(processed_data[0])}")
            
            # Try to call the method directly
            print("  Attempting to call _queue_plot_data...")
            c._queue_plot_data(processed_data)
            print("  ✓ _queue_plot_data succeeded")
            
        except Exception as e:
            print(f"  ✗ _queue_plot_data failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Additional debugging
            print("\n  Additional debugging info:")
            print(f"    c type: {type(c)}")
            print(f"    c._queue_plot_data type: {type(c._queue_plot_data)}")
            print(f"    processed_data type: {type(processed_data)}")
            if hasattr(processed_data, '__iter__'):
                print(f"    processed_data[0] type: {type(processed_data[0])}")
            
            return 1
        
    else:
        print("✗ 6824E not connected")
        return 1
    
    print("\n✓ _queue_plot_data method debug completed!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


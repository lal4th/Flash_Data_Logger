#!/usr/bin/env python3
"""
Debug the complete extended multi-channel data flow for 6824E.
"""

from __future__ import annotations

from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== Extended Multi-Channel Data Flow Debug ===")
    
    c = StreamingController()
    
    # Enable channels A, B, C, and D
    print("Enabling channels A, B, C, and D...")
    c.set_channel_a_config(True, 1, 8)  # enabled=True, coupling=DC, range=±10V
    c.set_channel_b_config(True, 1, 8)
    c.set_channel_c_config(True, 1, 8)
    c.set_channel_d_config(True, 1, 8)
    
    print(f"Enabled channels: {c._get_enabled_channels()}")
    
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
            import traceback
            traceback.print_exc()
            return 1
        
        # Test the _acquire_block method
        print("\nTesting _acquire_block...")
        try:
            block_data = c._acquire_block()
            print(f"  ✓ _acquire_block succeeded: {len(block_data)} samples")
            if block_data:
                print(f"  Sample data structure: {len(block_data[0])} elements per sample")
                print(f"  First sample: {block_data[0]}")
        except Exception as e:
            print(f"  ✗ _acquire_block failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
        # Test the _process_block method
        print("\nTesting _process_block...")
        try:
            processed_data = c._process_block(block_data)
            print(f"  ✓ _process_block succeeded: {len(processed_data)} samples")
            if processed_data:
                print(f"  Processed data structure: {len(processed_data[0])} elements per sample")
                print(f"  First processed sample: {processed_data[0]}")
        except Exception as e:
            print(f"  ✗ _process_block failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
        # Test the _queue_plot_data method
        print("\nTesting _queue_plot_data...")
        try:
            c._queue_plot_data(processed_data)
            print(f"  ✓ _queue_plot_data succeeded")
            
            # Check plot queue contents
            if not c._plot_queue.empty():
                plot_payload = c._plot_queue.get_nowait()
                print(f"  Plot payload structure: {len(plot_payload)} elements")
                print(f"  Plot payload: {plot_payload}")
            else:
                print("  Plot queue is empty")
        except Exception as e:
            print(f"  ✗ _queue_plot_data failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
    else:
        print("✗ 6824E not connected")
        return 1
    
    print("\n✓ Extended multi-channel data flow test completed successfully!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


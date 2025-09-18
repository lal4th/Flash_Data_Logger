#!/usr/bin/env python3
"""
Debug the data processing path to verify extended multi-channel data flows correctly.
"""

from __future__ import annotations

from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== Data Processing Path Debug ===")
    
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
            if block_data:
                print(f"  Sample data structure: {len(block_data[0])} elements per sample")
                print(f"  First sample: {block_data[0]}")
        except Exception as e:
            print(f"  ✗ _acquire_block failed: {e}")
            return 1
        
        # Test the _process_block method
        print("\nTesting _process_block...")
        try:
            processed_data = c._process_block(block_data)
            print(f"  ✓ _process_block succeeded: {len(processed_data)} samples")
            if processed_data:
                print(f"  Processed data structure: {len(processed_data[0])} elements per sample")
                print(f"  First processed sample: {processed_data[0]}")
                
                # Check if we have extended multi-channel data
                if len(processed_data[0]) == 10:  # Extended multi-channel: (timestamp, a, b, c, d, e, f, g, h, math_results)
                    print("  ✓ Processing EXTENDED MULTI-CHANNEL data (10 elements)")
                    # Extract channel data
                    timestamp, a, b, c, d, e, f, g, h, math_results = processed_data[0]
                    print(f"    Channel A: {a}")
                    print(f"    Channel B: {b}")
                    print(f"    Channel C: {c}")
                    print(f"    Channel D: {d}")
                    print(f"    Channel E: {e}")
                    print(f"    Channel F: {f}")
                    print(f"    Channel G: {g}")
                    print(f"    Channel H: {h}")
                elif len(processed_data[0]) == 4:  # Standard dual-channel: (timestamp, a, b, math_results)
                    print("  ❌ Processing STANDARD DUAL-CHANNEL data (4 elements)")
                else:
                    print(f"  ❓ Unknown processing path ({len(processed_data[0])} elements)")
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
                print(f"  Plot payload types: {[type(x).__name__ for x in plot_payload]}")
                print(f"  Plot payload shapes: {[x.shape if hasattr(x, 'shape') else len(x) for x in plot_payload]}")
                
                # Check if we have extended multi-channel plot data
                if len(plot_payload) == 9:  # Extended multi-channel: (a, b, c, d, e, f, g, h, timestamps)
                    print("  ✓ Plot queue contains EXTENDED MULTI-CHANNEL data (9 elements)")
                    # Check if channels C and D have data
                    data_c, data_d = plot_payload[2], plot_payload[3]
                    print(f"    Channel C data: {data_c[:3]}... (length: {len(data_c)})")
                    print(f"    Channel D data: {data_d[:3]}... (length: {len(data_d)})")
                elif len(plot_payload) == 3:  # Standard dual-channel: (a, b, timestamps)
                    print("  ❌ Plot queue contains STANDARD DUAL-CHANNEL data (3 elements)")
                else:
                    print(f"  ❓ Unknown plot payload format ({len(plot_payload)} elements)")
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
    
    print("\n✓ Data processing path debug completed!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


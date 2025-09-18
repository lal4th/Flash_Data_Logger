#!/usr/bin/env python3
"""
Debug the complete plot update flow from data acquisition to UI emission.
"""

from __future__ import annotations

from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== Complete Plot Update Flow Debug ===")
    
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
        
        # Test the complete flow: acquire -> process -> queue -> update
        print("\nTesting complete plot update flow...")
        try:
            # Step 1: Acquire data
            block_data = c._acquire_block()
            print(f"  ✓ _acquire_block: {len(block_data)} samples, {len(block_data[0])} elements per sample")
            
            # Step 2: Process data
            processed_data = c._process_block(block_data)
            print(f"  ✓ _process_block: {len(processed_data)} samples, {len(processed_data[0])} elements per sample")
            
            # Step 3: Queue plot data
            c._queue_plot_data(processed_data)
            print(f"  ✓ _queue_plot_data: succeeded")
            
            # Step 4: Check plot queue contents
            if not c._plot_queue.empty():
                plot_payload = c._plot_queue.get_nowait()
                print(f"  ✓ Plot queue: {len(plot_payload)} elements")
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
                print("  ❌ Plot queue is empty")
            
            # Step 5: Test _update_plot method
            print("\nTesting _update_plot method...")
            # Put the payload back in the queue for _update_plot to process
            c._plot_queue.put_nowait(plot_payload)
            c._update_plot()
            print(f"  ✓ _update_plot: succeeded")
            
        except Exception as e:
            print(f"  ✗ Complete plot update flow failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
    else:
        print("✗ 6824E not connected")
        return 1
    
    print("\n✓ Complete plot update flow debug completed!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


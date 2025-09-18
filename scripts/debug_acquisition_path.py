#!/usr/bin/env python3
"""
Debug which data acquisition path is being used in the controller.
"""

from __future__ import annotations

from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== Data Acquisition Path Debug ===")
    
    c = StreamingController()
    
    # Enable channels A, B, C, and D
    print("Enabling channels A, B, C, and D...")
    c.set_channel_a_config(True, 1, 8)
    c.set_channel_b_config(True, 1, 8)
    c.set_channel_c_config(True, 1, 8)
    c.set_channel_d_config(True, 1, 8)
    
    print(f"Enabled channels: {c._get_enabled_channels()}")
    print(f"Number of enabled channels: {len(c._get_enabled_channels())}")
    
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
        
        # Test the _acquire_block method with detailed logging
        print("\nTesting _acquire_block with detailed logging...")
        try:
            # Add debug logging to see which path is taken
            enabled_channels = c._get_enabled_channels()
            print(f"  Enabled channels: {enabled_channels}")
            print(f"  Number of enabled channels: {len(enabled_channels)}")
            print(f"  Has read_multi_channel method: {hasattr(c._source, 'read_multi_channel')}")
            
            block_data = c._acquire_block()
            print(f"  ✓ _acquire_block succeeded: {len(block_data)} samples")
            if block_data:
                print(f"  Sample data structure: {len(block_data[0])} elements per sample")
                print(f"  First sample: {block_data[0]}")
                
                # Determine which acquisition path was used based on data structure
                if len(block_data[0]) == 9:  # Extended multi-channel
                    print("  ✓ Using EXTENDED MULTI-CHANNEL acquisition path (9 elements)")
                elif len(block_data[0]) == 3:  # Standard dual-channel
                    print("  ❌ Using STANDARD DUAL-CHANNEL acquisition path (3 elements)")
                else:
                    print(f"  ❓ Unknown acquisition path ({len(block_data[0])} elements)")
        except Exception as e:
            print(f"  ✗ _acquire_block failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
    else:
        print("✗ 6824E not connected")
        return 1
    
    print("\n✓ Data acquisition path debug completed!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


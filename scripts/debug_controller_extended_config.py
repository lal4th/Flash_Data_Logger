#!/usr/bin/env python3
"""
Debug the StreamingController with extended channel configuration for channels C and D.
"""

from __future__ import annotations

from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== Controller Extended Config Debug ===")
    
    c = StreamingController()
    
    print("Initial config:")
    print(f"  Channel A enabled: {c._config.channel_a_enabled}")
    print(f"  Channel B enabled: {c._config.channel_b_enabled}")
    print(f"  Channel C enabled: {c._config.channel_c_enabled}")
    print(f"  Channel D enabled: {c._config.channel_d_enabled}")
    
    # Enable channels C and D
    print("\nEnabling channels C and D...")
    c._config.channel_c_enabled = True
    c._config.channel_d_enabled = True
    
    print("After enabling C and D:")
    print(f"  Channel C enabled: {c._config.channel_c_enabled}")
    print(f"  Channel D enabled: {c._config.channel_d_enabled}")
    
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
    else:
        print("✗ 6824E not connected")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


#!/usr/bin/env python3
"""
Debug the multi-channel data flow to see what happens when channels C and D are enabled.
"""

from __future__ import annotations

import time
from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== Multi-Channel Data Flow Debug ===")
    
    c = StreamingController()
    
    # Enable channels C and D
    c._config.channel_c_enabled = True
    c._config.channel_d_enabled = True
    
    print("Config:")
    print(f"  Channel A enabled: {c._config.channel_a_enabled}")
    print(f"  Channel B enabled: {c._config.channel_b_enabled}")
    print(f"  Channel C enabled: {c._config.channel_c_enabled}")
    print(f"  Channel D enabled: {c._config.channel_d_enabled}")
    
    # Setup the controller
    c.probe_device()
    
    if c._pico_6000_source:
        print("\nTesting data acquisition...")
        
        # Test read_dual_channel directly
        print("Testing read_dual_channel() directly:")
        try:
            (a_val, b_val), timestamp = c._pico_6000_source.read_dual_channel()
            print(f"  A: {a_val:.3f}V, B: {b_val:.3f}V, t: {timestamp:.3f}")
            print("  Note: read_dual_channel only returns A and B data")
        except Exception as e:
            print(f"  ✗ read_dual_channel failed: {e}")
        
        # Test the controller's acquisition loop
        print("\nTesting controller acquisition loop...")
        try:
            c.start()
            time.sleep(1.0)  # Let it run for 1 second
            c.stop()
            print("  ✓ Controller acquisition loop completed")
        except Exception as e:
            print(f"  ✗ Controller acquisition loop failed: {e}")
            import traceback
            traceback.print_exc()
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


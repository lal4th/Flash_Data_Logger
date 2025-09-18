#!/usr/bin/env python3
"""
Debug the UI-Controller integration to verify channels are enabled when plots are added.
"""

from __future__ import annotations

from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== UI-Controller Integration Debug ===")
    
    c = StreamingController()
    
    print("Initial config:")
    print(f"  Channel A enabled: {c._config.channel_a_enabled}")
    print(f"  Channel B enabled: {c._config.channel_b_enabled}")
    print(f"  Channel C enabled: {c._config.channel_c_enabled}")
    print(f"  Channel D enabled: {c._config.channel_d_enabled}")
    
    # Simulate adding plots for channels C and D (like the UI would do)
    print("\nSimulating UI adding plots for channels C and D...")
    
    # Enable channel C (like UI would call)
    c.set_channel_c_config(True, 1, 8)  # enabled=True, coupling=DC, range=±10V
    print(f"  After enabling C: Channel C enabled: {c._config.channel_c_enabled}")
    
    # Enable channel D (like UI would call)
    c.set_channel_d_config(True, 1, 8)  # enabled=True, coupling=DC, range=±10V
    print(f"  After enabling D: Channel D enabled: {c._config.channel_d_enabled}")
    
    # Test the controller setup with channels C and D enabled
    print("\nTesting controller setup with C and D enabled...")
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


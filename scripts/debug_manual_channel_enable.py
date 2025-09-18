#!/usr/bin/env python3
"""
Debug manually enabling channels C and D in the controller to see if it works.
"""

from __future__ import annotations

from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== Manual Channel Enable Debug ===")
    
    c = StreamingController()
    
    print("Initial config:")
    print(f"  Channel A enabled: {c._config.channel_a_enabled}")
    print(f"  Channel B enabled: {c._config.channel_b_enabled}")
    
    # Try to manually enable channels C and D by adding them to the config
    # This is a hack to test if the issue is just missing config settings
    
    # Check if we can add channel C and D settings to the config
    print("\nTrying to add channel C and D settings...")
    
    # Add channel C settings
    c._config.channel_c_enabled = True
    c._config.channel_c_coupling = 1
    c._config.channel_c_range = 8
    c._config.channel_c_offset = 0.0
    
    # Add channel D settings  
    c._config.channel_d_enabled = True
    c._config.channel_d_coupling = 1
    c._config.channel_d_range = 8
    c._config.channel_d_offset = 0.0
    
    print("After adding channel C and D settings:")
    print(f"  Channel C enabled: {c._config.channel_c_enabled}")
    print(f"  Channel D enabled: {c._config.channel_d_enabled}")
    
    # Check if the configure_multi_channel method can handle these
    print("\nTesting configure_multi_channel with C and D enabled...")
    
    c.probe_device()
    
    if c._pico_6000_source:
        try:
            # Try to call configure_multi_channel with the new settings
            # This will likely fail because the method doesn't know about C and D
            c._pico_6000_source.configure_multi_channel(
                sample_rate_hz=100,
                channel_a_enabled=True,
                channel_b_enabled=True,
                # channel_c_enabled=True,  # This parameter doesn't exist
                # channel_d_enabled=True,  # This parameter doesn't exist
            )
            print("  ✓ configure_multi_channel succeeded")
        except Exception as e:
            print(f"  ✗ configure_multi_channel failed: {e}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


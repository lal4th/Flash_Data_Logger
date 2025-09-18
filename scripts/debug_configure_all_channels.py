#!/usr/bin/env python3
"""
Debug configuring all channels C-H on 6824E to see if they can be enabled.
"""

from __future__ import annotations

from app.acquisition.pico_6000_direct import Pico6000DirectSource


def main() -> int:
    print("\n=== Configure All Channels Debug (6824E) ===")
    
    source = Pico6000DirectSource()
    
    if source.connect():
        print("✓ Connected to 6824E")
        
        # Try to configure all channels individually
        channels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        
        for i, channel_name in enumerate(channels):
            print(f"\nConfiguring channel {channel_name} (index {i}):")
            try:
                source.configure_channel(
                    channel=i,
                    enabled=True,
                    coupling=1,  # DC coupling
                    range_val=8  # ±10V range
                )
                print(f"  ✓ Channel {channel_name} configured successfully")
            except Exception as e:
                print(f"  ✗ Channel {channel_name} failed: {e}")
        
        # Test reading from all channels
        print("\nTesting read_dual_channel (should only return A and B):")
        try:
            (a_val, b_val), timestamp = source.read_dual_channel()
            print(f"  A: {a_val:.3f}V, B: {b_val:.3f}V, t: {timestamp:.3f}")
        except Exception as e:
            print(f"  ✗ read_dual_channel failed: {e}")
        
        source.disconnect()
    else:
        print("✗ Failed to connect to 6824E")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


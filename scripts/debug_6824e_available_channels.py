#!/usr/bin/env python3
"""
Debug what channels are available from the 6824E device.
"""

from __future__ import annotations

from app.acquisition.pico_6000_direct import Pico6000DirectSource


def main() -> int:
    print("\n=== 6824E Available Channels Debug ===")
    
    source = Pico6000DirectSource()
    
    if source.connect():
        print("✓ Connected to 6824E")
        
        # Get available channels
        available_channels = source.get_available_channels()
        print(f"Available channels: {available_channels}")
        
        # Check if the method exists and what it returns
        if hasattr(source, 'get_available_channels'):
            print(f"get_available_channels() method exists")
        else:
            print("get_available_channels() method does NOT exist")
        
        source.disconnect()
    else:
        print("✗ Failed to connect to 6824E")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


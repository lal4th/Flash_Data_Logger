#!/usr/bin/env python3
"""
Debug how the UI maps plot creation to controller channel configuration.
"""

from __future__ import annotations

from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== UI Channel Mapping Debug ===")
    
    c = StreamingController()
    
    print("Initial state:")
    print(f"  Available channels: {c._available_channels}")
    print(f"  Channel A enabled: {c._config.channel_a_enabled}")
    print(f"  Channel B enabled: {c._config.channel_b_enabled}")
    
    # Check if there are methods to enable additional channels
    print("\nController methods related to channels:")
    for attr in dir(c):
        if 'channel' in attr.lower() and not attr.startswith('_'):
            print(f"  {attr}")
    
    # Check if there are methods to configure additional channels
    print("\nController methods related to configuration:")
    for attr in dir(c):
        if 'config' in attr.lower() and not attr.startswith('_'):
            print(f"  {attr}")
    
    # Check if there are methods to set channel states
    print("\nController methods related to setting:")
    for attr in dir(c):
        if 'set' in attr.lower() and not attr.startswith('_'):
            print(f"  {attr}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


#!/usr/bin/env python3
"""
Debug StreamingConfig channel settings to understand why only A/B channels are enabled.
"""

from __future__ import annotations

from app.core.streaming_controller import StreamingController, StreamingConfig


def main() -> int:
    print("\n=== Config Channels Debug ===")
    
    # Create a fresh controller and inspect its config
    c = StreamingController()
    config = c._config
    
    print("StreamingConfig channel settings:")
    print(f"  multi_channel_mode: {config.multi_channel_mode}")
    print(f"  channel_a_enabled: {config.channel_a_enabled}")
    print(f"  channel_b_enabled: {config.channel_b_enabled}")
    print(f"  channel_a_coupling: {config.channel_a_coupling}")
    print(f"  channel_b_coupling: {config.channel_b_coupling}")
    print(f"  channel_a_range: {config.channel_a_range}")
    print(f"  channel_b_range: {config.channel_b_range}")
    print(f"  channel_a_offset: {config.channel_a_offset}")
    print(f"  channel_b_offset: {config.channel_b_offset}")
    
    # Check if there are any other channel settings
    print("\nAll config attributes:")
    for attr in dir(config):
        if not attr.startswith('_') and 'channel' in attr.lower():
            value = getattr(config, attr)
            print(f"  {attr}: {value}")
    
    # Check available channels
    print(f"\nAvailable channels: {c._available_channels}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


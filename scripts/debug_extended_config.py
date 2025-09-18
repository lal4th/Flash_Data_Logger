#!/usr/bin/env python3
"""
Debug the extended StreamingConfig to verify all channel settings are available.
"""

from __future__ import annotations

from app.core.streaming_controller import StreamingController, StreamingConfig


def main() -> int:
    print("\n=== Extended Config Debug ===")
    
    # Create a fresh controller and inspect its config
    c = StreamingController()
    config = c._config
    
    print("Extended StreamingConfig channel settings:")
    channels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    
    for channel in channels:
        enabled = getattr(config, f'channel_{channel.lower()}_enabled', 'NOT_FOUND')
        coupling = getattr(config, f'channel_{channel.lower()}_coupling', 'NOT_FOUND')
        range_val = getattr(config, f'channel_{channel.lower()}_range', 'NOT_FOUND')
        offset = getattr(config, f'channel_{channel.lower()}_offset', 'NOT_FOUND')
        
        print(f"  Channel {channel}: enabled={enabled}, coupling={coupling}, range={range_val}, offset={offset}")
    
    # Test setting some channels
    print("\nTesting channel C and D enablement:")
    config.channel_c_enabled = True
    config.channel_d_enabled = True
    
    print(f"  Channel C enabled: {config.channel_c_enabled}")
    print(f"  Channel D enabled: {config.channel_d_enabled}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


#!/usr/bin/env python3
"""
Debug what channels the StreamingController thinks are available after probe_device().
"""

from __future__ import annotations

from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== Controller Available Channels Debug ===")
    
    c = StreamingController()
    
    print("Before probe_device():")
    print(f"  _available_channels: {c._available_channels}")
    
    c.probe_device()
    
    print("After probe_device():")
    print(f"  _available_channels: {c._available_channels}")
    print(f"  _detected_device: {c._detected_device}")
    print(f"  _device_available: {c._device_available}")
    
    # Check if the controller has the right channels
    if c._pico_6000_source:
        device_channels = c._pico_6000_source.get_available_channels()
        print(f"  Device reports channels: {device_channels}")
        print(f"  Controller has channels: {c._available_channels}")
        print(f"  Channels match: {device_channels == c._available_channels}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


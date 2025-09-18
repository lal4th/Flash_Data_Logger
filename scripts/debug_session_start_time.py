#!/usr/bin/env python3
"""
Debug _session_start_time initialization for 6824E controller.
"""

from __future__ import annotations

import time
from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== Session Start Time Debug (6824E) ===")
    
    c = StreamingController()
    
    print(f"Initial _session_start_time: {c._session_start_time}")
    
    c.probe_device()
    print(f"After probe: _session_start_time: {c._session_start_time}")
    
    c.start()
    print(f"After start: _session_start_time: {c._session_start_time}")
    
    try:
        time.sleep(1.0)
    finally:
        c.stop()
    
    print(f"After stop: _session_start_time: {c._session_start_time}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


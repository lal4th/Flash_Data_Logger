#!/usr/bin/env python3
"""
Debug the start() method execution for 6824E controller.
"""

from __future__ import annotations

import time
from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== Start Method Debug (6824E) ===")
    
    c = StreamingController()
    
    print(f"Initial _session_start_time: {c._session_start_time}")
    
    c.probe_device()
    print(f"After probe: _session_start_time: {c._session_start_time}")
    
    print("Calling start()...")
    try:
        c.start()
        print(f"After start: _session_start_time: {c._session_start_time}")
        print(f"Acquisition thread alive: {c._acquisition_thread.is_alive() if c._acquisition_thread else 'None'}")
    except Exception as e:
        print(f"Exception in start(): {e}")
        import traceback
        traceback.print_exc()
    
    try:
        time.sleep(1.0)
    finally:
        print("Calling stop()...")
        c.stop()
        print(f"After stop: _session_start_time: {c._session_start_time}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


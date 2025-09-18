#!/usr/bin/env python3
"""
Exercise StreamingController with 6824E to detect premature disconnects.
"""

from __future__ import annotations

import time
from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== Controller Lifecycle (6824E) ===")
    c = StreamingController()

    # Probe and expect 6824E
    c.probe_device()
    # Start
    c.start()
    t0 = time.time()
    time.sleep(3.0)
    # Stop
    c.stop()
    t1 = time.time()
    print(f"Ran for {t1 - t0:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


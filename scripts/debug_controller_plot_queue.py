#!/usr/bin/env python3
"""
Inspect StreamingController._plot_queue payloads for 6824E.
"""

from __future__ import annotations

import time
from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== Plot Queue Inspect (6824E) ===")
    c = StreamingController()
    c.probe_device()
    c.start()
    try:
        time.sleep(1.0)
        pulled = 0
        while pulled < 5:
            while not c._plot_queue.empty():
                a, b, ts = c._plot_queue.get_nowait()
                print(f"len a={len(a)}, len b={len(b)}, t0={ts[0]:.3f}, tN={ts[-1]:.3f}")
                pulled += 1
            time.sleep(0.2)
    finally:
        c.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


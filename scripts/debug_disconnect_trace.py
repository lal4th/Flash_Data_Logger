#!/usr/bin/env python3
"""
Trace calls to Pico6000DirectSource.disconnect() during controller run.
"""

from __future__ import annotations

import traceback
import time
from app.core.streaming_controller import StreamingController
from app.acquisition.pico_6000_direct import Pico6000DirectSource

orig_disconnect = Pico6000DirectSource.disconnect

def traced_disconnect(self):
    print("\n*** TRACE: Pico6000DirectSource.disconnect called ***")
    traceback.print_stack()
    return orig_disconnect(self)


def main() -> int:
    print("\n=== Disconnect Trace (6824E) ===")
    Pico6000DirectSource.disconnect = traced_disconnect  # type: ignore
    try:
        c = StreamingController()
        c.probe_device()
        c.start()
        time.sleep(2.0)
        c.stop()
    finally:
        Pico6000DirectSource.disconnect = orig_disconnect  # type: ignore
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


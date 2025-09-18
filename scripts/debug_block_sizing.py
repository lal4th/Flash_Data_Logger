#!/usr/bin/env python3
"""
Log block sizing and emitted batch sizes for 6824E controller at 100 Hz.
"""

from __future__ import annotations

import time
from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== Block Sizing Debug (6824E) ===")
    c = StreamingController()

    # Monkeypatch acquire to print samples_per_block derived value
    orig_acquire = c._acquire_block  # type: ignore
    emitted_sizes = []

    def cap_acquire():
        blk = orig_acquire()
        print(f"acquired {len(blk)} samples in block")
        return blk

    c._acquire_block = cap_acquire  # type: ignore

    # Patch queue to record emitted sizes
    orig_queue_plot = c._queue_plot_data  # type: ignore

    def cap_queue(block):
        emitted_sizes.append(len(block))
        return orig_queue_plot(block)

    c._queue_plot_data = cap_queue  # type: ignore

    c.probe_device()
    c.start()
    try:
        time.sleep(2.0)
    finally:
        c.stop()

    if emitted_sizes:
        print("emitted batch sizes:", emitted_sizes[:10])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


#!/usr/bin/env python3
"""
Compare StreamingController processed timestamps vs emitted plot timestamps.
"""

from __future__ import annotations

import time
from typing import List, Tuple

from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== Processed vs Emitted (6824E) ===")
    c = StreamingController()

    processed_snapshots: List[List[Tuple[float, float, float]]] = []
    emitted_snapshots: List[Tuple[list, list, list]] = []

    # Monkeypatch to capture processed output and emitted payloads
    orig_process_block = c._process_block  # type: ignore[attr-defined]
    orig_queue_plot = c._queue_plot_data  # type: ignore[attr-defined]

    def cap_process(block):
        out = orig_process_block(block)
        # store (t,a,b)
        processed_snapshots.append([(d[0], d[1], d[2]) for d in out])
        return out

    def cap_queue(block):
        # block is (t,a,b,math)
        ts = [d[0] for d in block]
        av = [d[1] for d in block]
        bv = [d[2] for d in block]
        emitted_snapshots.append((av, bv, ts))
        return orig_queue_plot(block)

    c._process_block = cap_process  # type: ignore
    c._queue_plot_data = cap_queue  # type: ignore

    c.probe_device()
    c.start()
    try:
        time.sleep(2.0)
    finally:
        c.stop()

    # Print first few comparisons
    print(f"processed blocks: {len(processed_snapshots)} | emitted blocks: {len(emitted_snapshots)}")
    for i in range(min(5, len(processed_snapshots), len(emitted_snapshots))):
        p = processed_snapshots[i]
        e = emitted_snapshots[i]
        if p:
            print(f"  blk {i}: proc t0={p[0][0]:.3f}, tN={p[-1][0]:.3f}  |  emit t0={e[2][0]:.3f}, tN={e[2][-1]:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




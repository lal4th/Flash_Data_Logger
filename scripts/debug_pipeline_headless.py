#!/usr/bin/env python3
"""
Headless pipeline test mirroring the controller's 6824E data flow.

Goal: ensure timestamps are converted to relative and multi-channel data
structures are populated for downstream plotting/CSV.
"""

from __future__ import annotations

import time
from typing import List, Tuple

from app.acquisition.pico_6000_direct import Pico6000DirectSource


def main() -> int:
    print("\n=== Headless Pipeline (6824E) ===")
    src = Pico6000DirectSource()
    if not src.connect():
        print("Failed to connect to 6824E")
        return 1

    try:
        # Configure A/B for this test (extendable to more channels later)
        src.configure_channel(0, True, coupling=1, range_val=9)
        src.configure_channel(1, True, coupling=1, range_val=9)

        # Simulate the controller's session timing
        session_start_abs: float | None = None
        rel_ts: List[float] = []
        ch_a: List[float] = []
        ch_b: List[float] = []

        sample_rate_hz = 100
        for i in range(100):
            (ab, t_abs) = src.read_dual_channel()
            if session_start_abs is None:
                session_start_abs = t_abs
            t_rel = t_abs - session_start_abs
            rel_ts.append(t_rel)
            ch_a.append(ab[0])
            ch_b.append(ab[1])
            time.sleep(1.0 / sample_rate_hz)

        print(f"Samples: {len(rel_ts)}")
        print(f"First/last rel t: {rel_ts[0]:.3f} .. {rel_ts[-1]:.3f}")
        print(f"A stats: min={min(ch_a):.3f}, max={max(ch_a):.3f}")
        print(f"B stats: min={min(ch_b):.3f}, max={max(ch_b):.3f}")

        # Acceptance
        if rel_ts[0] > 0.01:
            print("Rel t does not start near 0 — investigate session start handling.")
        if rel_ts[-1] < 0.5:
            print("Rel t not increasing as expected — investigate blocking loop.")

        return 0
    finally:
        src.close()


if __name__ == "__main__":
    raise SystemExit(main())




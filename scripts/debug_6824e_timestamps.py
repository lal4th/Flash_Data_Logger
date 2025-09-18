#!/usr/bin/env python3
"""
Debug 6824E timestamps and relative-time conversion outside the GUI.

Collect a few blocks of readings via Pico6000DirectSource.read_dual_channel()
and verify that relative timestamps start at ~0 and advance monotonically.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Tuple

from app.acquisition.pico_6000_direct import Pico6000DirectSource


@dataclass
class BlockSummary:
    block_index: int
    n_samples: int
    abs_t_min: float
    abs_t_max: float
    rel_t_min: float
    rel_t_max: float
    rel_dt_avg_ms: float


def main() -> int:
    print("\n=== 6824E Timestamp Debug ===")

    src = Pico6000DirectSource()
    if not src.connect():
        print("Failed to connect to 6824E; aborting.")
        return 1

    try:
        # Configure two channels (A,B) for simplicity here; timestamp is shared
        src.configure_channel(0, True, coupling=1, range_val=9)
        src.configure_channel(1, True, coupling=1, range_val=9)

        sample_rate_hz = 100
        n_blocks = 5
        samples_per_block = 50

        # Establish session start at first sample time we see
        session_start_abs: float | None = None
        summaries: List[BlockSummary] = []

        for b in range(n_blocks):
            abs_ts: List[float] = []
            rel_ts: List[float] = []

            for _ in range(samples_per_block):
                (a_b, t_abs) = src.read_dual_channel()
                if session_start_abs is None:
                    session_start_abs = t_abs
                t_rel = t_abs - session_start_abs
                abs_ts.append(t_abs)
                rel_ts.append(t_rel)
                # Match requested cadence approximately
                time.sleep(1.0 / sample_rate_hz)

            # Summarize the block
            rel_deltas = [rel_ts[i] - rel_ts[i - 1] for i in range(1, len(rel_ts))]
            rel_dt_avg_ms = (sum(rel_deltas) / max(1, len(rel_deltas))) * 1000.0

            summaries.append(
                BlockSummary(
                    block_index=b,
                    n_samples=len(abs_ts),
                    abs_t_min=min(abs_ts),
                    abs_t_max=max(abs_ts),
                    rel_t_min=min(rel_ts),
                    rel_t_max=max(rel_ts),
                    rel_dt_avg_ms=rel_dt_avg_ms,
                )
            )

        print("\nSession start (abs):", session_start_abs)
        print("Block summaries:")
        for s in summaries:
            print(
                f"  Block {s.block_index}: n={s.n_samples} | "
                f"abs=[{s.abs_t_min:.6f}..{s.abs_t_max:.6f}] | "
                f"rel=[{s.rel_t_min:.3f}..{s.rel_t_max:.3f}] s | "
                f"avg dt={s.rel_dt_avg_ms:.2f} ms"
            )

        print("\nPASS CRITERIA:")
        print("- rel_t_min for first block is ~0.000")
        print("- rel_t_max increases across blocks")
        print("- avg dt ~= 10 ms for 100 Hz")

        return 0
    finally:
        src.close()


if __name__ == "__main__":
    raise SystemExit(main())




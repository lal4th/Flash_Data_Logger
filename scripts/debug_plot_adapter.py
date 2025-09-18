#!/usr/bin/env python3
"""
Validate plot X-axis behavior given relative vs absolute timestamps.
This does not use Qt; it emulates PlotPanel.update_data() range logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class PlotState:
    x_min: float
    x_max: float


def simulate_update(timestamps: List[float], timeline: float) -> PlotState:
    if not timestamps:
        return PlotState(0.0, timeline)
    max_time = float(timestamps[-1])
    if max_time <= timeline:
        return PlotState(0.0, max(timeline, max_time))
    else:
        return PlotState(max_time - timeline, max_time)


def main() -> int:
    print("\n=== Plot Adapter X-axis Debug ===")
    timeline = 10.0

    # Case 1: Relative timestamps starting at 0
    ts_rel = [i * 0.1 for i in range(30)]  # 0..2.9 s
    state_rel = simulate_update(ts_rel, timeline)
    print(f"Relative: x=[{state_rel.x_min:.3f}, {state_rel.x_max:.3f}]")

    # Case 2: Absolute epoch timestamps (bad input)
    epoch_base = 1_758_200_000.0
    ts_abs = [epoch_base + i * 0.1 for i in range(30)]
    state_abs = simulate_update(ts_abs, timeline)
    print(f"Absolute: x=[{state_abs.x_min:.3f}, {state_abs.x_max:.3f}]")

    print("\nPASS CRITERIA:")
    print("- Relative case should be [0, ~10] while < timeline; then roll when exceeded.")
    print("- Absolute case shows huge values; confirms need for relative conversion upstream.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




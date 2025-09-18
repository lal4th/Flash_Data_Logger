#!/usr/bin/env python3
"""
Validate CSV writer contract for multi-channel data: timestamps, headers, and values.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

from app.storage.csv_writer import CsvWriter


def main() -> int:
    print("\n=== CSV Writer Contract Debug ===")

    out = Path("cache/csv_contract_test.csv")
    channel_config: Dict[str, Any] = {
        "channel_a": {"range": 9, "coupling": 1, "offset": 0.0},
        "channel_b": {"range": 9, "coupling": 1, "offset": 0.0},
    }
    math_channels: Dict[str, Any] = {
        "Math 1": {"enabled": True, "title": "Math 1", "formula": "A+B"},
        "Math 2": {"enabled": True, "title": "Math 2", "formula": "A-B"},
    }

    writer = CsvWriter(out, multi_channel_mode=True, channel_config=channel_config, math_channels=math_channels)
    writer.open()

    # Generate a small deterministic dataset with relative timestamps starting at 0
    timestamps = [i * 0.01 for i in range(10)]  # 100 Hz for 10 samples
    ch_a = [0.1 * i for i in range(10)]
    ch_b = [0.05 * i for i in range(10)]
    math_list = [{"Math 1": a + b, "Math 2": a - b} for a, b in zip(ch_a, ch_b)]

    writer.write_multi_channel_batch(timestamps, ch_a, ch_b, math_list)
    writer.close()

    print(f"Wrote: {out}")
    print("Expect: first column in seconds from 0, with headers for Channel_A, Channel_B, Math 1, Math 2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




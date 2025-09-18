#!/usr/bin/env python3
"""
Debug 6824E channel configuration for channels A–H using Pico6000DirectSource.

Checks enabling/disabling each channel and reports status.
"""

from __future__ import annotations

from typing import List, Tuple

from app.acquisition.pico_6000_direct import Pico6000DirectSource


def main() -> int:
    print("\n=== 6824E Channel Config Debug (A–H) ===")

    src = Pico6000DirectSource()
    if not src.connect():
        print("Failed to connect to 6824E; aborting.")
        return 1

    try:
        channels = list(range(8))  # 0..7 → A..H
        results: List[Tuple[int, bool, str]] = []

        for ch in channels:
            ok = src.configure_channel(ch, True, coupling=1, range_val=9)
            results.append((ch, ok, "on"))
        for ch in channels:
            ok = src.configure_channel(ch, False)
            results.append((ch, ok, "off"))

        print("\nResults:")
        for ch, ok, state in results:
            label = chr(ord('A') + ch)
            print(f"  Channel {label} ({ch}) {state}: {'OK' if ok else 'FAIL'}")

        return 0
    finally:
        src.close()


if __name__ == "__main__":
    raise SystemExit(main())




from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional


class CsvWriter:
    def __init__(self, path: Path) -> None:
        self._path = Path(path)
        self._file: Optional[object] = None
        self._writer: Optional[csv.writer] = None

    def open(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self._path.open("w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow(["timestamp", "value"])  # header

    def write_row(self, timestamp: float, value: float) -> None:
        if not self._writer:
            return
        # Format timestamp to show seconds with appropriate precision
        # For high sample rates, show more decimal places
        if timestamp < 0.001:  # Less than 1ms
            timestamp_str = f"{timestamp:.9f}"
        elif timestamp < 1.0:  # Less than 1 second
            timestamp_str = f"{timestamp:.6f}"
        else:  # 1 second or more
            timestamp_str = f"{timestamp:.3f}"
        self._writer.writerow([timestamp_str, f"{value:.6f}"])

    def write_batch(self, timestamps: list[float], values: list[float]) -> None:
        """Write multiple rows in a single batch for better performance."""
        if not self._writer or not timestamps or not values:
            return
        
        # Prepare batch data
        rows = []
        for timestamp, value in zip(timestamps, values):
            # Format timestamp to show seconds with appropriate precision
            if timestamp < 0.001:  # Less than 1ms
                timestamp_str = f"{timestamp:.9f}"
            elif timestamp < 1.0:  # Less than 1 second
                timestamp_str = f"{timestamp:.6f}"
            else:  # 1 second or more
                timestamp_str = f"{timestamp:.3f}"
            rows.append([timestamp_str, f"{value:.6f}"])
        
        # Write all rows at once
        self._writer.writerows(rows)
        # Flush to ensure data is written to disk
        if self._file:
            self._file.flush()

    def close(self) -> None:
        if self._file:
            self._file.close()
            self._file = None
            self._writer = None



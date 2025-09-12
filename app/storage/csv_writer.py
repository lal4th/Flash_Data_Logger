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
        self._writer.writerow([f"{timestamp:.9f}", f"{value:.9f}"])

    def close(self) -> None:
        if self._file:
            self._file.close()
            self._file = None
            self._writer = None



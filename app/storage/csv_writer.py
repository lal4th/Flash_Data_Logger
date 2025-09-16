from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class CsvWriter:
    def __init__(self, path: Path, multi_channel_mode: bool = False, channel_config: Optional[Dict[str, Any]] = None) -> None:
        self._path = Path(path)
        self._file: Optional[object] = None
        self._writer: Optional[csv.writer] = None
        self._multi_channel_mode = multi_channel_mode
        self._channel_config = channel_config or {}
        self._header_written = False

    def open(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self._path.open("w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        
        if self._multi_channel_mode:
            self._write_multi_channel_header()
        else:
            self._writer.writerow(["timestamp", "value"])  # Single channel header
            self._header_written = True

    def _write_multi_channel_header(self) -> None:
        """Write comprehensive header for multi-channel CSV format."""
        if not self._writer:
            return
        
        # Write file information header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._writer.writerow([f"# Flash Data Logger v0.7 - Multi-Channel Data"])
        self._writer.writerow([f"# Timestamp: {timestamp}"])
        
        # Write channel configuration
        if 'channel_a' in self._channel_config:
            ch_a = self._channel_config['channel_a']
            range_info = self._get_range_info(ch_a.get('range', 8))
            coupling = "DC" if ch_a.get('coupling', 1) else "AC"
            self._writer.writerow([f"# Channel A: {range_info}, {coupling}, Offset: {ch_a.get('offset', 0.0):.3f}V"])
        
        if 'channel_b' in self._channel_config:
            ch_b = self._channel_config['channel_b']
            range_info = self._get_range_info(ch_b.get('range', 8))
            coupling = "DC" if ch_b.get('coupling', 1) else "AC"
            self._writer.writerow([f"# Channel B: {range_info}, {coupling}, Offset: {ch_b.get('offset', 0.0):.3f}V"])
        
        # Write column headers
        self._writer.writerow(["timestamp", "Channel_A", "Channel_B"])
        self._header_written = True

    def _get_range_info(self, range_index: int) -> str:
        """Get voltage range information string."""
        ranges = {
            0: "±10mV", 1: "±20mV", 2: "±50mV", 3: "±100mV", 4: "±200mV",
            5: "±500mV", 6: "±1V", 7: "±2V", 8: "±5V", 9: "±10V"
        }
        return ranges.get(range_index, f"Range_{range_index}")

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

    def write_multi_channel_row(self, timestamp: float, channel_a_value: float, channel_b_value: float) -> None:
        """Write a single row of multi-channel data."""
        if not self._writer or not self._header_written:
            return
        
        # Format timestamp to show seconds with appropriate precision
        if timestamp < 0.001:  # Less than 1ms
            timestamp_str = f"{timestamp:.9f}"
        elif timestamp < 1.0:  # Less than 1 second
            timestamp_str = f"{timestamp:.6f}"
        else:  # 1 second or more
            timestamp_str = f"{timestamp:.3f}"
        
        self._writer.writerow([timestamp_str, f"{channel_a_value:.6f}", f"{channel_b_value:.6f}"])

    def write_multi_channel_batch(self, timestamps: list[float], channel_a_values: list[float], channel_b_values: list[float]) -> None:
        """Write multiple rows of multi-channel data in a single batch for better performance."""
        if not self._writer or not self._header_written or not timestamps:
            return
        
        # Prepare batch data
        rows = []
        for timestamp, ch_a_val, ch_b_val in zip(timestamps, channel_a_values, channel_b_values):
            # Format timestamp to show seconds with appropriate precision
            if timestamp < 0.001:  # Less than 1ms
                timestamp_str = f"{timestamp:.9f}"
            elif timestamp < 1.0:  # Less than 1 second
                timestamp_str = f"{timestamp:.6f}"
            else:  # 1 second or more
                timestamp_str = f"{timestamp:.3f}"
            rows.append([timestamp_str, f"{ch_a_val:.6f}", f"{ch_b_val:.6f}"])
        
        # Write all rows at once
        self._writer.writerows(rows)
        # Flush to ensure data is written to disk
        if self._file:
            self._file.flush()

    def set_channel_config(self, channel_config: Dict[str, Any]) -> None:
        """Update channel configuration for header information."""
        self._channel_config = channel_config

    def close(self) -> None:
        if self._file:
            self._file.close()
            self._file = None
            self._writer = None



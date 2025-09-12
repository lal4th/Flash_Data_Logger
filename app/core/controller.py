from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PyQt6 import QtCore

from app.acquisition.source import AcquisitionSource, DummySineSource
from app.acquisition.pico_direct import PicoDirectSource, test_device_connection
from app.processing.pipeline import ProcessingPipeline
from app.storage.csv_writer import CsvWriter


class ControllerSignals(QtCore.QObject):
    signal_status = QtCore.pyqtSignal(str)
    signal_plot = QtCore.pyqtSignal(object)


@dataclass
class ControllerConfig:
    sample_rate_hz: int = 100
    filename: Path = Path("data.csv")
    recording_enabled: bool = False
    channel: int = 0
    coupling: int = 1  # 1=DC, 0=AC for ps4000
    voltage_range: int = 7  # ±5 V
    resolution_bits: int = 16


class AppController(QtCore.QObject):
    signal_status = QtCore.pyqtSignal(str)
    signal_plot = QtCore.pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self._config = ControllerConfig()
        self._source: AcquisitionSource = DummySineSource()
        self._pipeline = ProcessingPipeline()
        self._writer: Optional[CsvWriter] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._device_available: bool = False

    # ----- Config setters -----
    def set_sample_rate(self, hz: int) -> None:
        # Clamp to a reasonable device-aware range for ps4000 streaming
        min_hz = 1
        max_hz = 1_000_000
        clamped = int(max(min_hz, min(max_hz, hz)))
        self._config.sample_rate_hz = clamped
        if clamped != hz:
            self.signal_status.emit(f"Sample rate clamped to: {clamped} Hz")
        else:
            self.signal_status.emit(f"Sample rate set: {clamped} Hz")

    def set_channel(self, channel_index: int) -> None:
        self._config.channel = int(channel_index)
        self.signal_status.emit(f"Channel: {'AB'[channel_index] if channel_index in (0, 1) else channel_index}")

    def set_coupling(self, coupling: int) -> None:
        # 1=DC, 0=AC according to ps4000SetChannel
        self._config.coupling = 1 if coupling else 0
        self.signal_status.emit("Coupling: DC" if self._config.coupling == 1 else "Coupling: AC")

    def set_voltage_range(self, range_enum: int) -> None:
        self._config.voltage_range = int(range_enum)
        self.signal_status.emit(f"Range enum: {self._config.voltage_range}")

    def set_resolution(self, bits: int) -> None:
        self._config.resolution_bits = int(bits)
        self.signal_status.emit(f"Resolution: {bits} bit")

    def set_filename(self, filename: Path) -> None:
        self._config.filename = filename
        self.signal_status.emit(f"Filename: {filename}")

    def set_recording(self, enabled: bool) -> None:
        self._config.recording_enabled = enabled
        self.signal_status.emit("Recording: ON" if enabled else "Recording: OFF")

    # ----- Lifecycle -----
    def probe_device(self) -> None:
        """Test PicoScope DLL availability without opening device (to avoid popup)."""
        success, message = test_device_connection()
        self._device_available = success
        if success:
            self.signal_status.emit(f"✓ {message}")
        else:
            self.signal_status.emit(f"⚠ {message}")

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        # Use our fresh, proven implementation
        source_msg = ""
        try:
            self._source = PicoDirectSource()
            self._source.configure(
                sample_rate_hz=self._config.sample_rate_hz,
                channel=self._config.channel,
                coupling=self._config.coupling,
                voltage_range=self._config.voltage_range,
                resolution_bits=self._config.resolution_bits,
            )
            source_msg = "Using Pico source (ps4000)"
        except Exception as ex:
            # Surface exact error details as required for Phase 1
            error_msg = str(ex)
            dll_info = ""
            if hasattr(self._source, 'get_diagnostics'):
                try:
                    dll_info = f" — {self._source.get_diagnostics()}"
                except:
                    pass
            
            source_msg = f"Pico init failed: {error_msg}{dll_info} — using dummy"
            self._source = DummySineSource()

        try:
            self._source.configure(
                sample_rate_hz=self._config.sample_rate_hz,
                channel=self._config.channel,
                coupling=self._config.coupling,
                voltage_range=self._config.voltage_range,
                resolution_bits=self._config.resolution_bits,
            )
        except Exception:
            pass
        if self._config.recording_enabled:
            self._writer = CsvWriter(self._config.filename)
            self._writer.open()
        else:
            self._writer = None
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        if source_msg:
            self.signal_status.emit(source_msg + " — Running…")
        # Do not overwrite the previous detailed status about which source is active

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
        try:
            self._source.close()
        except Exception:
            pass
        if self._writer:
            self._writer.close()
            self._writer = None
        self.signal_status.emit("Stopped")

    def reset_data(self) -> None:
        """Reset data source counters for a fresh start."""
        if hasattr(self._source, '_sample_count'):
            self._source._sample_count = 0
            self._source._start_time = None
        self.signal_status.emit("Data reset")

    # ----- Worker loop -----
    def _run_loop(self) -> None:
        period = 1.0 / float(self._config.sample_rate_hz)
        next_tick = time.perf_counter()
        buffer_time: list[float] = []
        buffer_data: list[float] = []

        while not self._stop_event.is_set():
            now = time.perf_counter()
            if now < next_tick:
                time.sleep(max(0.0, next_tick - now))
                continue
            next_tick += period

            # Acquire
            value, timestamp = self._source.read()
            # Process
            value = self._pipeline.process(value)

            # Record in-memory buffers for plotting (timestamp is already relative to 0)
            buffer_time.append(timestamp)
            buffer_data.append(value)

            # Persist
            if self._writer:
                self._writer.write_row(timestamp, value)

            # Plot update throttled to ~30 FPS
            if len(buffer_data) >= max(5, self._config.sample_rate_hz // 30):
                data = np.asarray(buffer_data, dtype=float)
                time_axis = np.asarray(buffer_time, dtype=float)
                self.signal_plot.emit((data, time_axis))
                # keep last few seconds
                keep = self._config.sample_rate_hz * 5
                if len(buffer_data) > keep:
                    del buffer_data[:-keep]
                    del buffer_time[:-keep]



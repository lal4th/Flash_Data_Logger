from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

import numpy as np
from PyQt6 import QtCore

from app.acquisition.source import AcquisitionSource
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
    voltage_range: int = 8  # ±10 V (changed from ±5V to prevent saturation)
    resolution_bits: int = 16
    cache_directory: Path = Path.cwd() / "cache"
    y_min: float = -10.0  # Will be updated based on voltage range
    y_max: float = 10.0   # Will be updated based on voltage range
    timeline_seconds: float = 60.0


class AppController(QtCore.QObject):
    signal_status = QtCore.pyqtSignal(str)
    signal_plot = QtCore.pyqtSignal(object)
    signal_clear_plot = QtCore.pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._config = ControllerConfig()
        self._source: Optional[AcquisitionSource] = None
        self._pico_source: Optional[PicoDirectSource] = None
        self._pipeline = ProcessingPipeline()
        self._writer: Optional[CsvWriter] = None
        self._cache_writer: Optional[CsvWriter] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._device_available: bool = False
        self._session_start_time: Optional[datetime] = None

    # ----- Config setters -----
    def set_sample_rate(self, hz: int) -> None:
        # Clamp to a reasonable device-aware range for ps4000 streaming
        # Limit to 1000 Hz for better stability (2000 Hz was still causing crashes)
        min_hz = 1
        max_hz = 1000  # Further reduced from 2000 to prevent crashes
        clamped = int(max(min_hz, min(max_hz, hz)))
        self._config.sample_rate_hz = clamped
        
        # Warn about high sample rates that might cause performance issues
        if clamped > 500:
            self.signal_status.emit(f"Sample rate set: {clamped} Hz (High rate - performance may be affected)")
        elif clamped != hz:
            self.signal_status.emit(f"Sample rate clamped to: {clamped} Hz (max: 1000 Hz)")
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

    def set_cache_directory(self, directory: Path) -> None:
        self._config.cache_directory = directory
        self.signal_status.emit(f"Cache directory: {directory}")

    def set_y_range(self, y_min: float, y_max: float) -> None:
        self._config.y_min = y_min
        self._config.y_max = y_max
        self.signal_status.emit(f"Y-axis range: {y_min:.1f} to {y_max:.1f} V")

    def set_timeline(self, timeline_seconds: float) -> None:
        self._config.timeline_seconds = timeline_seconds
        self.signal_status.emit(f"Timeline: {timeline_seconds:.1f} seconds")

    def _create_cache_filename(self) -> Path:
        """Create timestamped cache filename."""
        if self._session_start_time is None:
            self._session_start_time = datetime.now()
        timestamp_str = self._session_start_time.strftime("%Y_%m_%d_%H.%M.%S")
        return self._config.cache_directory / f"Flash_Data_Logger_CSV_{timestamp_str}.csv"

    # ----- Lifecycle -----
    def probe_device(self) -> None:
        """Test PicoScope DLL availability and open device once (popup acceptable at startup)."""
        success, message = test_device_connection()
        self._device_available = success
        if success:
            # Create and open the PicoDirectSource once at startup
            try:
                self._pico_source = PicoDirectSource()
                # Configure with default settings to open the device
                self._pico_source.configure(
                    sample_rate_hz=self._config.sample_rate_hz,
                    channel=self._config.channel,
                    coupling=self._config.coupling,
                    voltage_range=self._config.voltage_range,
                    resolution_bits=self._config.resolution_bits,
                )
                self.signal_status.emit(f"✓ {message} (device opened)")
            except Exception as ex:
                self._pico_source = None
                self.signal_status.emit(f"⚠ {message} - Device open failed: {ex}")
        else:
            self.signal_status.emit(f"⚠ {message}")

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        
        # Clear the plot for fresh session first
        self.signal_clear_plot.emit()
        
        # Reset data source counters for fresh session
        self.reset_data()
        
        # Reuse existing PicoDirectSource if available, otherwise create new one
        source_msg = ""
        if self._pico_source is not None:
            # Reuse the device that was opened at startup
            self._source = self._pico_source
            try:
                # Just reconfigure the existing device (no new device open)
                self._source.configure(
                    sample_rate_hz=self._config.sample_rate_hz,
                    channel=self._config.channel,
                    coupling=self._config.coupling,
                    voltage_range=self._config.voltage_range,
                    resolution_bits=self._config.resolution_bits,
                )
                source_msg = "Using Pico source (ps4000) - device reused"
            except Exception as ex:
                self.signal_status.emit(f"Failed to start: Pico reconfigure failed: {ex}")
                return
        else:
            # Create new source - no fallback
            try:
                self._source = PicoDirectSource()
                self._source.configure(
                    sample_rate_hz=self._config.sample_rate_hz,
                    channel=self._config.channel,
                    coupling=self._config.coupling,
                    voltage_range=self._config.voltage_range,
                    resolution_bits=self._config.resolution_bits,
                )
                source_msg = "Using Pico source (ps4000) - new device"
            except Exception as ex:
                self.signal_status.emit(f"Failed to start: Pico init failed: {ex}")
                return
        
        # Always create cache CSV file
        cache_filename = self._create_cache_filename()
        self._cache_writer = CsvWriter(cache_filename)
        self._cache_writer.open()
        
        # No longer need user CSV file since we always cache
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
        
        # Only close the source if it's not our persistent PicoDirectSource
        if self._source is not self._pico_source:
            try:
                self._source.close()
            except Exception:
                pass
        
        if self._cache_writer:
            self._cache_writer.close()
            self._cache_writer = None
        self.signal_status.emit("Stopped")

    def reset_data(self) -> None:
        """Reset data source counters for a fresh start."""
        # Reset the persistent PicoDirectSource if it exists
        if self._pico_source is not None:
            if hasattr(self._pico_source, 'reset_session'):
                self._pico_source.reset_session()
            else:
                # Fallback for other source types
                self._pico_source._sample_count = 0
                self._pico_source._start_time = None
                if hasattr(self._pico_source, '_buffer_start_sample'):
                    self._pico_source._buffer_start_sample = 0
        # Also reset current source if it's different
        if hasattr(self._source, 'reset_session'):
            self._source.reset_session()
        elif hasattr(self._source, '_sample_count'):
            self._source._sample_count = 0
            self._source._start_time = None
            if hasattr(self._source, '_buffer_start_sample'):
                self._source._buffer_start_sample = 0
        self.signal_status.emit("Data reset")

    def save_cache_csv(self, destination_path: Path) -> bool:
        """Save the current cache CSV to a user-specified location."""
        # Check if we have a cache writer or if we can find the last cache file
        cache_path = None
        
        if self._cache_writer:
            # Cache writer is active, use it
            cache_path = self._cache_writer._path
            self._cache_writer.close()
            self._cache_writer = None
        else:
            # Look for the most recent cache file
            cache_dir = self._config.cache_directory
            if cache_dir.exists():
                cache_files = list(cache_dir.glob("Flash_Data_Logger_CSV_*.csv"))
                if cache_files:
                    # Get the most recent file
                    cache_path = max(cache_files, key=lambda f: f.stat().st_mtime)
        
        if not cache_path or not cache_path.exists():
            self.signal_status.emit("No data to save - start data acquisition first")
            return False
        
        try:
            # Copy the cache file to the destination
            import shutil
            shutil.copy2(cache_path, destination_path)
            
            self.signal_status.emit(f"CSV saved to: {destination_path}")
            return True
        except Exception as e:
            self.signal_status.emit(f"Failed to save CSV: {e}")
            return False

    def cleanup(self) -> None:
        """Clean up resources when application shuts down."""
        self.stop()
        if self._pico_source is not None:
            try:
                self._pico_source.close()
            except Exception:
                pass
            self._pico_source = None

    # ----- Worker loop -----
    def _run_loop(self) -> None:
        period = 1.0 / float(self._config.sample_rate_hz)
        next_tick = time.perf_counter()
        buffer_time: list[float] = []
        buffer_data: list[float] = []
        
        # CSV batch writing for high sample rates - ultra-aggressive batching for extreme rates
        if self._config.sample_rate_hz <= 100:
            csv_batch_size = 10
        elif self._config.sample_rate_hz <= 500:
            csv_batch_size = 50
        elif self._config.sample_rate_hz <= 1000:
            csv_batch_size = 100
        else:  # 1000+ Hz - ultra-aggressive batching
            csv_batch_size = 500  # Much larger batches for very high rates
        
        csv_batch_time: list[float] = []
        csv_batch_data: list[float] = []
        
        # Plot update frequency - ultra-conservative for high sample rates
        if self._config.sample_rate_hz <= 100:
            plot_update_interval = 10
        elif self._config.sample_rate_hz <= 500:
            plot_update_interval = 25
        elif self._config.sample_rate_hz <= 1000:
            plot_update_interval = 50
        else:  # 1000+ Hz - ultra-conservative updates
            plot_update_interval = 200  # Very infrequent updates for extreme rates

        try:
            sample_count = 0
            while not self._stop_event.is_set():
                now = time.perf_counter()
                if now < next_tick:
                    time.sleep(max(0.0, next_tick - now))
                    continue
                next_tick += period

                # Acquire
                try:
                    value, timestamp = self._source.read()
                    # Process
                    value = self._pipeline.process(value)
                    sample_count += 1
                    
                    # Performance monitoring for high sample rates
                    if self._config.sample_rate_hz > 500 and sample_count % 1000 == 0:
                        self.signal_status.emit(f"Performance: {sample_count} samples acquired at {self._config.sample_rate_hz} Hz")
                        
                except Exception as e:
                    self.signal_status.emit(f"Data acquisition error: {e}")
                    continue

                # Record in-memory buffers for plotting (timestamp is already relative to 0)
                buffer_time.append(timestamp)
                buffer_data.append(value)
                
                # Batch CSV data
                csv_batch_time.append(timestamp)
                csv_batch_data.append(value)
                
                # Show first few data points in status
                if len(buffer_data) <= 5:
                    self.signal_status.emit(f"Data point {len(buffer_data)}: {value:.4f}V at {timestamp:.6f}s")

                # Write CSV in batches to improve performance
                if len(csv_batch_data) >= csv_batch_size and self._cache_writer:
                    self._cache_writer.write_batch(csv_batch_time, csv_batch_data)
                    csv_batch_time.clear()
                    csv_batch_data.clear()

                # Plot update with adaptive frequency
                if len(buffer_data) >= plot_update_interval:
                    data = np.asarray(buffer_data, dtype=float)
                    time_axis = np.asarray(buffer_time, dtype=float)
                    self.signal_plot.emit((data, time_axis))
                    
                    # Keep data for the specified timeline plus some buffer for scrolling
                    # More aggressive memory management for high sample rates
                    if self._config.sample_rate_hz <= 500:
                        max_samples = int(self._config.sample_rate_hz * (self._config.timeline_seconds + 5))
                    else:  # High sample rates - more aggressive memory management
                        max_samples = int(self._config.sample_rate_hz * (self._config.timeline_seconds + 2))
                    
                    if len(buffer_data) > max_samples:
                        del buffer_data[:-max_samples]
                        del buffer_time[:-max_samples]
        finally:
            # Write any remaining CSV batch data
            if csv_batch_data and self._cache_writer:
                self._cache_writer.write_batch(csv_batch_time, csv_batch_data)



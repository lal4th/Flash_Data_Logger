"""
Streaming-based controller with RAM storage and background CSV writing.
This implements the optimal architecture identified through testing.
"""

from __future__ import annotations

import threading
import time
import queue
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime
import collections

import numpy as np
from PyQt6 import QtCore

from app.acquisition.source import AcquisitionSource
from app.acquisition.pico_direct import PicoDirectSource, test_device_connection
from app.processing.pipeline import ProcessingPipeline
from app.storage.csv_writer import CsvWriter


@dataclass
class StreamingConfig:
    sample_rate_hz: int = 100
    filename: Path = Path("data.csv")
    recording_enabled: bool = False
    channel: int = 0
    coupling: int = 1  # 1=DC, 0=AC for ps4000
    voltage_range: int = 8  # ±10 V (default range)
    resolution_bits: int = 16
    cache_directory: Path = Path.cwd() / "cache"
    y_min: float = -10.0  # Will be updated based on voltage range
    y_max: float = 10.0   # Will be updated based on voltage range
    timeline_seconds: float = 60.0
    # Streaming-specific settings
    block_size: int = 1000  # Samples per block
    ram_buffer_size_mb: int = 100  # Maximum RAM buffer size
    csv_write_interval_s: float = 1.0  # Write CSV every N seconds
    plot_update_rate_hz: float = 100.0  # Maximum plot update rate for real-time responsiveness
    # v0.7 Multi-channel settings
    multi_channel_mode: bool = False
    channel_a_enabled: bool = True
    channel_a_coupling: int = 1
    channel_a_range: int = 8
    channel_a_offset: float = 0.0
    channel_b_enabled: bool = True
    channel_b_coupling: int = 1
    channel_b_range: int = 8
    channel_b_offset: float = 0.0


class StreamingController(QtCore.QObject):
    """Streaming-based controller with optimal architecture for high sample rates."""
    
    signal_status = QtCore.pyqtSignal(str)
    signal_plot = QtCore.pyqtSignal(object)
    signal_clear_plot = QtCore.pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._config = StreamingConfig()
        self._source: Optional[AcquisitionSource] = None
        self._pico_source: Optional[PicoDirectSource] = None
        self._pipeline = ProcessingPipeline()
        
        # Streaming architecture components
        self._acquisition_thread: Optional[threading.Thread] = None
        self._csv_writer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Thread-safe data queues
        self._data_queue = queue.Queue(maxsize=100)  # Block data queue
        self._plot_queue = queue.Queue(maxsize=10)   # Plot data queue
        
        # RAM storage - v0.7 multi-channel support
        self._ram_buffer: List[Tuple[float, float, float]] = []  # (timestamp, channel_a, channel_b)
        self._ram_buffer_lock = threading.Lock()
        
        # CSV writing
        self._csv_writer: Optional[CsvWriter] = None
        self._csv_queue = queue.Queue()
        
        # Performance monitoring
        self._samples_acquired = 0
        self._samples_processed = 0
        self._samples_saved = 0
        self._session_start_time: Optional[datetime] = None
        
        # Channel offset storage (default 0 for both channels)
        self._channel_offsets = {0: 0.0, 1: 0.0}  # Channel A and B offsets
        
        # v0.7 Multi-channel data structures
        self._multi_channel_data: List[Tuple[float, float, float]] = []  # (timestamp, channel_a, channel_b)
        self._multi_channel_lock = threading.Lock()

    # ----- Config setters -----
    def set_sample_rate(self, hz: int) -> None:
        # No artificial limits - let the architecture handle high rates
        self._config.sample_rate_hz = max(1, int(hz))
        
        # Adjust block size based on sample rate for optimal performance
        if hz <= 100:
            self._config.block_size = 100
        elif hz <= 1000:
            self._config.block_size = 500
        elif hz <= 5000:
            self._config.block_size = 1000
        else:
            self._config.block_size = 2000
        
        self.signal_status.emit(f"Sample rate set: {self._config.sample_rate_hz} Hz (block size: {self._config.block_size})")

    def set_channel(self, channel_index: int) -> None:
        self._config.channel = int(channel_index)
        self.signal_status.emit(f"Channel: {'AB'[channel_index] if channel_index in (0, 1) else channel_index}")

    def set_coupling(self, coupling: int) -> None:
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

    # v0.7 Multi-channel configuration methods
    def set_multi_channel_mode(self, enabled: bool) -> None:
        """Enable or disable multi-channel mode."""
        self._config.multi_channel_mode = enabled
        self.signal_status.emit(f"Multi-channel mode: {'ON' if enabled else 'OFF'}")

    def set_channel_a_config(self, enabled: bool, coupling: int, voltage_range: int, offset: float = 0.0) -> None:
        """Configure Channel A settings."""
        self._config.channel_a_enabled = enabled
        self._config.channel_a_coupling = coupling
        self._config.channel_a_range = voltage_range
        self._config.channel_a_offset = offset
        self.signal_status.emit(f"Channel A: {'ON' if enabled else 'OFF'}, Range: {voltage_range}, Coupling: {'DC' if coupling else 'AC'}")

    def set_channel_b_config(self, enabled: bool, coupling: int, voltage_range: int, offset: float = 0.0) -> None:
        """Configure Channel B settings."""
        self._config.channel_b_enabled = enabled
        self._config.channel_b_coupling = coupling
        self._config.channel_b_range = voltage_range
        self._config.channel_b_offset = offset
        self.signal_status.emit(f"Channel B: {'ON' if enabled else 'OFF'}, Range: {voltage_range}, Coupling: {'DC' if coupling else 'AC'}")

    def get_multi_channel_config(self) -> dict:
        """Get current multi-channel configuration."""
        return {
            'multi_channel_mode': self._config.multi_channel_mode,
            'channel_a': {
                'enabled': self._config.channel_a_enabled,
                'coupling': self._config.channel_a_coupling,
                'range': self._config.channel_a_range,
                'offset': self._config.channel_a_offset
            },
            'channel_b': {
                'enabled': self._config.channel_b_enabled,
                'coupling': self._config.channel_b_coupling,
                'range': self._config.channel_b_range,
                'offset': self._config.channel_b_offset
            }
        }

    def zero_offset(self) -> None:
        """Zero the offset for the current channel by taking 100 samples and averaging them."""
        if self._acquisition_thread and self._acquisition_thread.is_alive():
            self.signal_status.emit("Cannot zero offset while acquisition is running - stop first")
            return
        
        if self._pico_source is None:
            self.signal_status.emit("Cannot zero offset - no device available")
            return
        
        try:
            self.signal_status.emit("Zeroing offset... taking 100 samples")
            
            # Take 100 samples from the current channel
            samples = []
            for _ in range(100):
                try:
                    value, _ = self._pico_source.read()
                    samples.append(value)
                except Exception as e:
                    self.signal_status.emit(f"Error taking sample: {e}")
                    return
            
            # Calculate average and store as offset
            if samples:
                average_offset = sum(samples) / len(samples)
                current_channel = self._config.channel
                self._channel_offsets[current_channel] = -average_offset  # Negative to cancel out the offset
                
                channel_name = "A" if current_channel == 0 else "B"
                self.signal_status.emit(f"Channel {channel_name} offset set to {self._channel_offsets[current_channel]:.6f} V")
            else:
                self.signal_status.emit("Failed to collect samples for offset calculation")
                
        except Exception as e:
            self.signal_status.emit(f"Zero offset failed: {e}")

    def get_channel_offset(self, channel: int) -> float:
        """Get the current offset for a specific channel."""
        return self._channel_offsets.get(channel, 0.0)

    def _create_cache_filename(self) -> Path:
        """Create timestamped cache filename with unique timestamp for each session."""
        # Always create a new timestamp for each session
        session_time = datetime.now()
        timestamp_str = session_time.strftime("%Y_%m_%d_%H.%M.%S")
        return self._config.cache_directory / f"Flash_Data_Logger_CSV_{timestamp_str}.csv"

    # ----- Lifecycle -----
    def probe_device(self) -> None:
        """Test PicoScope DLL availability and open device once."""
        success, message = test_device_connection()
        if success:
            try:
                self._pico_source = PicoDirectSource()
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
        """Start streaming acquisition with optimal architecture."""
        if self._acquisition_thread and self._acquisition_thread.is_alive():
            return
        
        self._stop_event.clear()
        
        # Clear the plot for fresh session
        self.signal_clear_plot.emit()
        
        # Reset counters
        self._samples_acquired = 0
        self._samples_processed = 0
        self._samples_saved = 0
        
        # Clear accumulated plot data
        self._accumulated_plot_data_a = []
        self._accumulated_plot_data_b = []
        self._accumulated_plot_timestamps = []
        
        # Reset data source counters for fresh session
        self.reset_data()
        
        # Setup data source - this will raise an exception if PicoScope is not available
        try:
            source_msg = self._setup_data_source()
        except Exception as ex:
            self.signal_status.emit(f"Failed to start: {ex}")
            return
        
        # Setup CSV writer
        cache_filename = self._create_cache_filename()
        if self._config.multi_channel_mode:
            # Multi-channel CSV writer with configuration
            channel_config = self.get_multi_channel_config()
            self._csv_writer = CsvWriter(cache_filename, multi_channel_mode=True, channel_config=channel_config)
        else:
            # Single channel CSV writer (v0.6 compatibility)
            self._csv_writer = CsvWriter(cache_filename, multi_channel_mode=False)
        self._csv_writer.open()
        
        # Start background threads
        self._acquisition_thread = threading.Thread(target=self._acquisition_loop, daemon=True)
        self._csv_writer_thread = threading.Thread(target=self._csv_writer_loop, daemon=True)
        
        self._acquisition_thread.start()
        self._csv_writer_thread.start()
        
        # Start plot update timer
        self._start_plot_timer()
        
        self.signal_status.emit(f"{source_msg} — Streaming at {self._config.sample_rate_hz} Hz...")

    def stop(self) -> None:
        """Stop streaming acquisition."""
        self._stop_event.set()
        
        # Stop plot timer
        self._stop_plot_timer()
        
        # Wait for threads to finish
        if self._acquisition_thread:
            self._acquisition_thread.join(timeout=2)
        if self._csv_writer_thread:
            self._csv_writer_thread.join(timeout=2)
        
        # Close CSV writer
        if self._csv_writer:
            self._csv_writer.close()
            self._csv_writer = None
        
        # Write remaining RAM data to CSV
        self._flush_ram_to_csv()
        
        self.signal_status.emit("Stopped")

    def reset_data(self) -> None:
        """Comprehensive reset that clears all data and saves current session."""
        # Stop any running acquisition first
        if self._acquisition_thread and self._acquisition_thread.is_alive():
            self.stop()
            time.sleep(0.1)  # Give threads time to stop
        
        # Save current CSV session to cache if we have data
        if self._csv_writer or len(self._ram_buffer) > 0:
            try:
                # Flush any remaining RAM data to CSV
                self._flush_ram_to_csv()
                
                # Close current CSV writer to finalize the file
                if self._csv_writer:
                    self._csv_writer.close()
                    self._csv_writer = None
                    
                self.signal_status.emit("Previous session saved to cache")
            except Exception as e:
                self.signal_status.emit(f"Warning: Could not save session: {e}")
        
        # Clear all data storage
        with self._ram_buffer_lock:
            self._ram_buffer.clear()
        
        # Clear accumulated plot data
        self._accumulated_plot_data_a = []
        self._accumulated_plot_data_b = []
        self._accumulated_plot_timestamps = []
        
        # Clear all queues
        while not self._data_queue.empty():
            try:
                self._data_queue.get_nowait()
            except:
                break
        while not self._plot_queue.empty():
            try:
                self._plot_queue.get_nowait()
            except:
                break
        while not self._csv_queue.empty():
            try:
                self._csv_queue.get_nowait()
            except:
                break
        
        # Reset counters
        self._samples_acquired = 0
        self._samples_processed = 0
        self._samples_saved = 0
        self._session_start_time = None
        
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
        
        self.signal_status.emit("All data cleared - ready for fresh session")

    def cleanup(self) -> None:
        """Clean up resources when application shuts down."""
        self.stop()
        if self._pico_source is not None:
            try:
                self._pico_source.close()
            except Exception:
                pass
            self._pico_source = None

    # ----- Streaming Architecture Implementation -----
    def _setup_data_source(self) -> str:
        """Setup the data source for streaming. Requires real PicoScope connection."""
        if self._pico_source is not None:
            # Reuse the device that was opened at startup
            self._source = self._pico_source
            try:
                if self._config.multi_channel_mode:
                    # Configure for multi-channel acquisition
                    self._source.configure_multi_channel(
                        sample_rate_hz=self._config.sample_rate_hz,
                        channel_a_enabled=self._config.channel_a_enabled,
                        channel_a_coupling=self._config.channel_a_coupling,
                        channel_a_range=self._config.channel_a_range,
                        channel_a_offset=self._config.channel_a_offset,
                        channel_b_enabled=self._config.channel_b_enabled,
                        channel_b_coupling=self._config.channel_b_coupling,
                        channel_b_range=self._config.channel_b_range,
                        channel_b_offset=self._config.channel_b_offset,
                        resolution_bits=self._config.resolution_bits,
                    )
                    return "Using Pico source (ps4000) - multi-channel mode"
                else:
                    # Configure for single channel acquisition (v0.6 compatibility)
                    self._source.configure(
                        sample_rate_hz=self._config.sample_rate_hz,
                        channel=self._config.channel,
                        coupling=self._config.coupling,
                        voltage_range=self._config.voltage_range,
                        resolution_bits=self._config.resolution_bits,
                    )
                    return "Using Pico source (ps4000) - single channel mode"
            except Exception as ex:
                raise RuntimeError(f"Pico reconfigure failed: {ex}")
        else:
            # Create new source - no fallback
            try:
                self._source = PicoDirectSource()
                if self._config.multi_channel_mode:
                    # Configure for multi-channel acquisition
                    self._source.configure_multi_channel(
                        sample_rate_hz=self._config.sample_rate_hz,
                        channel_a_enabled=self._config.channel_a_enabled,
                        channel_a_coupling=self._config.channel_a_coupling,
                        channel_a_range=self._config.channel_a_range,
                        channel_a_offset=self._config.channel_a_offset,
                        channel_b_enabled=self._config.channel_b_enabled,
                        channel_b_coupling=self._config.channel_b_coupling,
                        channel_b_range=self._config.channel_b_range,
                        channel_b_offset=self._config.channel_b_offset,
                        resolution_bits=self._config.resolution_bits,
                    )
                    return "Using Pico source (ps4000) - new device, multi-channel mode"
                else:
                    # Configure for single channel acquisition (v0.6 compatibility)
                    self._source.configure(
                        sample_rate_hz=self._config.sample_rate_hz,
                        channel=self._config.channel,
                        coupling=self._config.coupling,
                        voltage_range=self._config.voltage_range,
                        resolution_bits=self._config.resolution_bits,
                    )
                    return "Using Pico source (ps4000) - new device, single channel mode"
            except Exception as ex:
                raise RuntimeError(f"Pico init failed: {ex}")

    def _acquisition_loop(self) -> None:
        """Main acquisition loop using block-based streaming."""
        try:
            # Use maximum block acquisition rate for real-time responsiveness
            # This ensures plot updates respond immediately to signal changes
            block_acquisition_rate_hz = 100.0  # Acquire blocks at 100 Hz for maximum responsiveness
            block_duration = 1.0 / block_acquisition_rate_hz
            next_block_time = time.perf_counter()
            
            while not self._stop_event.is_set():
                current_time = time.perf_counter()
                if current_time < next_block_time:
                    time.sleep(max(0.0, next_block_time - current_time))
                    continue
                
                # Acquire a block of data
                block_data = self._acquire_block()
                if block_data:
                    # Process the block
                    processed_block = self._process_block(block_data)
                    
                    # Store in RAM
                    self._store_block_in_ram(processed_block)
                    
                    # Queue for plot updates
                    self._queue_plot_data(processed_block)
                    
                    # Queue for CSV writing
                    self._queue_csv_data(processed_block)
                    
                    self._samples_acquired += len(processed_block)
                
                next_block_time += block_duration
                
        except Exception as e:
            # Connection lost or acquisition error - stop the session
            self.signal_status.emit(f"Connection lost: {e}")
            # Trigger stop behavior
            self._stop_event.set()

    def _acquire_block(self) -> List[Tuple[float, float, float]]:
        """Acquire a block of data from the source."""
        block_data = []
        try:
            # Calculate samples per block based on sample rate and acquisition rate
            # This ensures we keep up with the data rate at high sample rates
            block_acquisition_rate_hz = 100.0  # Fixed acquisition rate
            samples_per_block = max(1, int(self._config.sample_rate_hz / block_acquisition_rate_hz))
            
            # Limit block size for responsiveness (max 50 samples per block)
            samples_per_block = min(samples_per_block, 50)
            
            for _ in range(samples_per_block):
                if self._stop_event.is_set():
                    break
                
                if self._config.multi_channel_mode:
                    # Multi-channel acquisition
                    (channel_a_value, channel_b_value), timestamp = self._source.read_dual_channel()
                    block_data.append((timestamp, channel_a_value, channel_b_value))
                else:
                    # Single channel acquisition (v0.6 compatibility)
                    value, timestamp = self._source.read()
                    block_data.append((timestamp, value, 0.0))  # Channel B = 0 for single channel
        except Exception as e:
            # Connection lost during block acquisition - propagate the error
            raise RuntimeError(f"Block acquisition failed: {e}")
        
        return block_data

    def _process_block(self, block_data: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
        """Process a block of multi-channel data."""
        processed_data = []
        try:
            # Get channel offsets
            channel_a_offset = self._channel_offsets.get(0, 0.0)
            channel_b_offset = self._channel_offsets.get(1, 0.0)
            
            for timestamp, channel_a_value, channel_b_value in block_data:
                # Apply channel offsets: (raw voltage + offset)
                offset_adjusted_a = channel_a_value + channel_a_offset
                offset_adjusted_b = channel_b_value + channel_b_offset
                
                # For now, bypass processing pipeline to avoid voltage smoothing issues
                # TODO: Implement proper multi-channel processing pipeline
                processed_a = offset_adjusted_a
                processed_b = offset_adjusted_b
                
                processed_data.append((timestamp, processed_a, processed_b))
                self._samples_processed += 1
        except Exception as e:
            self.signal_status.emit(f"Block processing error: {e}")
            return block_data  # Return unprocessed data if processing fails
        
        return processed_data

    def _store_block_in_ram(self, block_data: List[Tuple[float, float, float]]) -> None:
        """Store block data in RAM buffer."""
        with self._ram_buffer_lock:
            self._ram_buffer.extend(block_data)
            
            # Limit RAM buffer size
            max_samples = int(self._config.ram_buffer_size_mb * 1024 * 1024 / 24)  # ~24 bytes per sample (timestamp + 2 channels)
            if len(self._ram_buffer) > max_samples:
                # Remove oldest data
                excess = len(self._ram_buffer) - max_samples
                self._ram_buffer = self._ram_buffer[excess:]

    def _queue_plot_data(self, block_data: List[Tuple[float, float, float]]) -> None:
        """Queue block data for plot updates."""
        try:
            # Convert to numpy arrays for efficient plotting
            timestamps = np.array([d[0] for d in block_data], dtype=float)
            channel_a_values = np.array([d[1] for d in block_data], dtype=float)
            channel_b_values = np.array([d[2] for d in block_data], dtype=float)
            
            # Non-blocking put - store both channels
            self._plot_queue.put_nowait((channel_a_values, channel_b_values, timestamps))
        except queue.Full:
            # Plot queue is full, skip this update
            pass

    def _queue_csv_data(self, block_data: List[Tuple[float, float, float]]) -> None:
        """Queue block data for CSV writing."""
        try:
            # Non-blocking put
            self._csv_queue.put_nowait(block_data)
        except queue.Full:
            # CSV queue is full, this is a problem
            self.signal_status.emit("Warning: CSV queue full - data may be lost")

    def _csv_writer_loop(self) -> None:
        """Background thread for CSV writing."""
        while not self._stop_event.is_set():
            try:
                # Get data from queue with timeout
                block_data = self._csv_queue.get(timeout=0.1)
                
                # Write to CSV
                if self._csv_writer:
                    timestamps = [d[0] for d in block_data]
                    channel_a_values = [d[1] for d in block_data]
                    channel_b_values = [d[2] for d in block_data]
                    
                    if self._config.multi_channel_mode:
                        # Multi-channel CSV writing
                        self._csv_writer.write_multi_channel_batch(timestamps, channel_a_values, channel_b_values)
                    else:
                        # Single channel CSV writing (v0.6 compatibility)
                        # Use channel A values for single channel mode
                        self._csv_writer.write_batch(timestamps, channel_a_values)
                    
                    self._samples_saved += len(block_data)
                
                self._csv_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.signal_status.emit(f"CSV writing error: {e}")

    def _start_plot_timer(self) -> None:
        """Start the plot update timer at fixed 10 Hz rate."""
        # Use a simple threading approach instead of QTimer for better compatibility
        # Plot updates at fixed 10 Hz regardless of data acquisition sample rate
        self._plot_timer_running = True
        self._plot_timer_thread = threading.Thread(target=self._plot_timer_loop, daemon=True)
        self._plot_timer_thread.start()

    def _stop_plot_timer(self) -> None:
        """Stop the plot update timer."""
        if hasattr(self, '_plot_timer_running'):
            self._plot_timer_running = False
        if hasattr(self, '_plot_timer_thread') and self._plot_timer_thread:
            self._plot_timer_thread.join(timeout=0.5)

    def _plot_timer_loop(self) -> None:
        """Plot timer loop running in background thread."""
        plot_update_period = 1.0 / self._config.plot_update_rate_hz
        while self._plot_timer_running:
            try:
                self._update_plot()
                time.sleep(0.001)  # Minimal sleep for maximum responsiveness (1ms)
            except Exception as e:
                self.signal_status.emit(f"Plot timer error: {e}")
                break

    def _update_plot(self) -> None:
        """Update the plot with accumulated multi-channel data for continuous display."""
        try:
            # Collect all available plot data
            all_channel_a_values = []
            all_channel_b_values = []
            all_timestamps = []
            
            while not self._plot_queue.empty():
                try:
                    channel_a_values, channel_b_values, timestamps = self._plot_queue.get_nowait()
                    all_channel_a_values.extend(channel_a_values)
                    all_channel_b_values.extend(channel_b_values)
                    all_timestamps.extend(timestamps)
                except queue.Empty:
                    break
            
            if all_channel_a_values:
                # Add to accumulated plot data
                if not hasattr(self, '_accumulated_plot_data_a'):
                    self._accumulated_plot_data_a = []
                    self._accumulated_plot_data_b = []
                    self._accumulated_plot_timestamps = []
                
                self._accumulated_plot_data_a.extend(all_channel_a_values)
                self._accumulated_plot_data_b.extend(all_channel_b_values)
                self._accumulated_plot_timestamps.extend(all_timestamps)
                
                # Limit accumulated data to timeline + buffer
                # Use a fixed calculation based on timeline, not sample rate
                # This ensures plot behavior is independent of sample rate
                # Use a reasonable fixed limit based on timeline duration
                max_samples = int(100000)  # Fixed limit: ~100k samples should be enough for any timeline
                if len(self._accumulated_plot_data_a) > max_samples:
                    excess = len(self._accumulated_plot_data_a) - max_samples
                    self._accumulated_plot_data_a = self._accumulated_plot_data_a[excess:]
                    self._accumulated_plot_data_b = self._accumulated_plot_data_b[excess:]
                    self._accumulated_plot_timestamps = self._accumulated_plot_timestamps[excess:]
                
                # Convert to numpy arrays and emit based on mode
                data_a = np.array(self._accumulated_plot_data_a, dtype=float)
                data_b = np.array(self._accumulated_plot_data_b, dtype=float)
                time_axis = np.array(self._accumulated_plot_timestamps, dtype=float)
                
                if self._config.multi_channel_mode:
                    # Emit multi-channel plot data: (data_a, data_b, time_axis)
                    self.signal_plot.emit((data_a, data_b, time_axis))
                else:
                    # Emit single-channel plot data: (data, time_axis) - use Channel A data
                    self.signal_plot.emit((data_a, time_axis))
                
        except Exception as e:
            self.signal_status.emit(f"Plot update error: {e}")

    def _flush_ram_to_csv(self) -> None:
        """Flush remaining RAM data to CSV."""
        with self._ram_buffer_lock:
            if self._ram_buffer and self._csv_writer:
                timestamps = [d[0] for d in self._ram_buffer]
                channel_a_values = [d[1] for d in self._ram_buffer]
                channel_b_values = [d[2] for d in self._ram_buffer]
                
                if self._config.multi_channel_mode:
                    # Multi-channel CSV writing
                    self._csv_writer.write_multi_channel_batch(timestamps, channel_a_values, channel_b_values)
                else:
                    # Single channel CSV writing (v0.6 compatibility)
                    # Use channel A values for single channel mode
                    self._csv_writer.write_batch(timestamps, channel_a_values)
                
                self._samples_saved += len(self._ram_buffer)
                self._ram_buffer.clear()

    def save_cache_csv(self, destination_path: Path) -> bool:
        """Save the current cache CSV to a user-specified location."""
        try:
            # Check if we have a cache writer or if we can find the last cache file
            cache_path = None
            
            if self._csv_writer:
                # Cache writer is active, use it
                cache_path = self._csv_writer._path
                # Close the current writer to ensure all data is written
                self._csv_writer.close()
                self._csv_writer = None
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
            
            # Copy the cache file to the destination
            import shutil
            shutil.copy2(cache_path, destination_path)
            
            self.signal_status.emit(f"CSV saved to: {destination_path}")
            return True
            
        except Exception as e:
            self.signal_status.emit(f"Failed to save CSV: {e}")
            return False

    def get_performance_stats(self) -> dict:
        """Get current performance statistics."""
        return {
            'samples_acquired': self._samples_acquired,
            'samples_processed': self._samples_processed,
            'samples_saved': self._samples_saved,
            'ram_buffer_size': len(self._ram_buffer),
            'data_queue_size': self._data_queue.qsize(),
            'plot_queue_size': self._plot_queue.qsize(),
            'csv_queue_size': self._csv_queue.qsize(),
        }

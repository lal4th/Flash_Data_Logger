"""
Fresh PicoScope 4262 implementation using ONLY the proven smoke test approach.
No Python wrappers, no complex detection - just direct DLL calls that we know work.
"""

import ctypes
import os
import time
from typing import Tuple, Optional
import numpy as np

from app.acquisition.source import AcquisitionSource
from app.acquisition.voltage_converter import PicoScopeVoltageConverter


def find_ps4000_dll() -> str:
    """Find ps4000.dll using the exact same approach as the working smoke test."""
    search_paths = [
        r"C:\Program Files\Pico Technology",
        r"C:\Program Files (x86)\Pico Technology",
    ]
    
    dll_name = "ps4000.dll"
    
    for base_path in search_paths:
        if os.path.exists(base_path):
            # Recursively search for ps4000.dll
            for root, dirs, files in os.walk(base_path):
                if dll_name in files:
                    dll_path = os.path.join(root, dll_name)
                    return dll_path
    
    raise RuntimeError(f"{dll_name} not found in search paths: {search_paths}")


def test_device_connection() -> Tuple[bool, str]:
    """Test if we can open the PicoScope device at startup (accept popup here)."""
    try:
        dll_path = find_ps4000_dll()
        
        # Add DLL directory to PATH for dependency resolution
        dll_dir = os.path.dirname(dll_path)
        old_path = os.environ.get('PATH', '')
        os.environ['PATH'] = dll_dir + os.pathsep + old_path
        
        # Also try adding to DLL directory for Windows DLL search
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(dll_dir)
        
        try:
            ps4000 = ctypes.CDLL(dll_path)
        except OSError as e:
            return False, f"Failed to load DLL {dll_path}: {e}"

        # Test opening the device (popup acceptable at startup)
        handle = ctypes.c_int16()
        status = ps4000.ps4000OpenUnit(ctypes.byref(handle))
        
        if status == 0:
            # Success! Close it immediately 
            ps4000.ps4000CloseUnit(handle)
            return True, f"PicoScope 4262 detected (DLL: {dll_path})"
        else:
            # Common status codes
            status_codes = {
                3: "PICO_NOT_FOUND - Device not found or PicoScope app running",
                4: "PICO_INVALID_PARAMETER",
                13: "PICO_INVALID_PARAMETER", 
                23: "PICO_USB_3_0_DEVICE_NON_USB_3_0_PORT",
                268435457: "DLL dependency issue"
            }
            error_desc = status_codes.get(status, f"Unknown status {status}")
            return False, f"Device open failed: {error_desc} (status={status}, DLL={dll_path})"
            
    except Exception as e:
        return False, f"Detection failed: {e}"


class PicoDirectSource(AcquisitionSource):
    """Direct PicoScope 4262 source using ONLY the proven smoke test approach."""

    def __init__(self) -> None:
        self._sample_rate_hz: int = 100
        self._handle = ctypes.c_int16(0)
        self._opened = False
        self._buf: Optional[np.ndarray] = None
        self._buf_idx = 0
        self._lib: Optional[ctypes.CDLL] = None
        self._channel: int = 0
        self._coupling: int = 1
        self._range: int = 7
        self._dll_path: Optional[str] = None
        self._start_time: Optional[float] = None
        self._sample_count: int = 0
        self._actual_sample_interval_s: float = 0.01  # Default 100Hz
        self._buffer_start_sample: int = 0
        # Initialize the voltage converter with the mathematically correct formula
        self._voltage_converter = PicoScopeVoltageConverter()
        
        # v0.7 Multi-channel support
        self._multi_channel_mode: bool = False
        self._channel_a_config = {'enabled': True, 'coupling': 1, 'range': 8, 'offset': 0.0}
        self._channel_b_config = {'enabled': True, 'coupling': 1, 'range': 8, 'offset': 0.0}
        self._dual_channel_buf: Optional[Tuple[np.ndarray, np.ndarray]] = None  # (channel_a_data, channel_b_data)
        self._dual_channel_buf_idx = 0

    def configure(
        self,
        *,
        sample_rate_hz: int,
        channel: int = 0,
        coupling: int = 1,
        voltage_range: int = 7,
        resolution_bits: int = 16,
    ) -> None:
        self._sample_rate_hz = max(1, int(sample_rate_hz))
        self._channel = int(channel)
        self._coupling = int(coupling)
        self._range = int(voltage_range)
        # Reset timing counters on reconfigure
        self._start_time = None
        self._sample_count = 0
        self._buffer_start_sample = 0
        # Clear any existing buffer data
        self._buf = None
        self._buf_idx = 0
        self._dual_channel_buf = None
        self._dual_channel_buf_idx = 0
        
        # If device is already open, reconfigure it
        if self._opened and self._lib is not None:
            self._reconfigure_device()
        else:
            self._ensure_open()

    def configure_multi_channel(
        self,
        *,
        sample_rate_hz: int,
        channel_a_enabled: bool = True,
        channel_a_coupling: int = 1,
        channel_a_range: int = 8,
        channel_a_offset: float = 0.0,
        channel_b_enabled: bool = True,
        channel_b_coupling: int = 1,
        channel_b_range: int = 8,
        channel_b_offset: float = 0.0,
        resolution_bits: int = 16,
    ) -> None:
        """Configure dual-channel acquisition for v0.7."""
        self._sample_rate_hz = max(1, int(sample_rate_hz))
        self._multi_channel_mode = True
        
        # Configure Channel A
        self._channel_a_config = {
            'enabled': channel_a_enabled,
            'coupling': int(channel_a_coupling),
            'range': int(channel_a_range),
            'offset': float(channel_a_offset)
        }
        
        # Configure Channel B
        self._channel_b_config = {
            'enabled': channel_b_enabled,
            'coupling': int(channel_b_coupling),
            'range': int(channel_b_range),
            'offset': float(channel_b_offset)
        }
        
        # Reset timing counters on reconfigure
        self._start_time = None
        self._sample_count = 0
        self._buffer_start_sample = 0
        # Clear any existing buffer data
        self._buf = None
        self._buf_idx = 0
        self._dual_channel_buf = None
        self._dual_channel_buf_idx = 0
        
        # If device is already open, reconfigure it
        if self._opened and self._lib is not None:
            self._reconfigure_multi_channel_device()
        else:
            self._ensure_multi_channel_open()

    def read(self) -> Tuple[float, float]:
        if self._multi_channel_mode:
            return self._read_multi_channel()
        else:
            return self._read_single_channel()

    def _read_single_channel(self) -> Tuple[float, float]:
        """Read single channel data (v0.6 compatibility)."""
        self._ensure_open()
        if self._buf is None or self._buf_idx >= len(self._buf):
            try:
                self._capture_block()
            except Exception as e:
                return 0.0, 0.0
        if self._buf is None or len(self._buf) == 0:
            return 0.0, 0.0
        
        # Initialize start time on first read
        if self._start_time is None:
            self._start_time = time.perf_counter()
        
        value = float(self._buf[self._buf_idx])
        
        # Calculate proper timestamp: buffer start + position within buffer
        # Use the desired sample rate interval, not the actual PicoScope interval
        current_sample_number = self._buffer_start_sample + self._buf_idx
        desired_interval_s = 1.0 / self._sample_rate_hz
        timestamp = current_sample_number * desired_interval_s
        
        self._buf_idx += 1
        
        # Update global sample count continuously
        self._sample_count = current_sample_number + 1
        
        return value, timestamp

    def _read_multi_channel(self) -> Tuple[Tuple[float, float], float]:
        """Read dual-channel data (v0.7 new functionality)."""
        self._ensure_multi_channel_open()
        if self._dual_channel_buf is None or self._dual_channel_buf_idx >= len(self._dual_channel_buf[0]):
            try:
                self._capture_dual_channel_block()
            except Exception as e:
                return (0.0, 0.0), 0.0
        
        if self._dual_channel_buf is None or len(self._dual_channel_buf[0]) == 0:
            return (0.0, 0.0), 0.0
        
        # Initialize start time on first read
        if self._start_time is None:
            self._start_time = time.perf_counter()
        
        # Get values from both channels
        channel_a_value = float(self._dual_channel_buf[0][self._dual_channel_buf_idx])
        channel_b_value = float(self._dual_channel_buf[1][self._dual_channel_buf_idx])
        
        # Calculate proper timestamp
        current_sample_number = self._buffer_start_sample + self._dual_channel_buf_idx
        desired_interval_s = 1.0 / self._sample_rate_hz
        timestamp = current_sample_number * desired_interval_s
        
        self._dual_channel_buf_idx += 1
        
        # Update global sample count continuously
        self._sample_count = current_sample_number + 1
        
        return (channel_a_value, channel_b_value), timestamp

    def read_dual_channel(self) -> Tuple[Tuple[float, float], float]:
        """Read dual-channel data and return (channel_a, channel_b), timestamp."""
        return self._read_multi_channel()

    def _ensure_open(self) -> None:
        if self._opened:
            return

        # Find the DLL
        dll_path = find_ps4000_dll()
        self._dll_path = dll_path
        
        # Add DLL directory to PATH for dependency resolution
        dll_dir = os.path.dirname(dll_path)
        old_path = os.environ.get('PATH', '')
        os.environ['PATH'] = dll_dir + os.pathsep + old_path
        
        # Also try adding to DLL directory for Windows DLL search
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(dll_dir)
        
        try:
            ps4000 = ctypes.CDLL(dll_path)
        except OSError as e:
            raise RuntimeError(f"Failed to load DLL {dll_path}: {e}")

        # Open the device (exact same as smoke test)
        handle = ctypes.c_int16()
        status = ps4000.ps4000OpenUnit(ctypes.byref(handle))
        
        if status != 0:
            status_codes = {
                3: "PICO_NOT_FOUND - Device not found or PicoScope app running",
                4: "PICO_INVALID_PARAMETER",
                13: "PICO_INVALID_PARAMETER", 
                23: "PICO_USB_3_0_DEVICE_NON_USB_3_0_PORT",
                268435457: "DLL dependency issue"
            }
            error_desc = status_codes.get(status, f"Unknown status {status}")
            raise RuntimeError(f"ps4000OpenUnit failed: {error_desc} (status={status}, DLL={dll_path})")
        
        self._handle = handle
        self._lib = ps4000
        
        # Configure Channel
        status = ps4000.ps4000SetChannel(
            handle,
            ctypes.c_int32(self._channel),
            ctypes.c_int16(1),  # enabled
            ctypes.c_int32(self._coupling),
            ctypes.c_int32(self._range),
            ctypes.c_float(0.0)  # analogue_offset - try 0.0 first
        )
        
        if status != 0:
            ps4000.ps4000CloseUnit(handle)
            raise RuntimeError(f"ps4000SetChannel failed with status: {status}")
        
        self._opened = True

    def _ensure_multi_channel_open(self) -> None:
        """Open device and configure both channels for dual-channel acquisition."""
        if self._opened:
            return

        # Find the DLL
        dll_path = find_ps4000_dll()
        self._dll_path = dll_path
        
        # Add DLL directory to PATH for dependency resolution
        dll_dir = os.path.dirname(dll_path)
        old_path = os.environ.get('PATH', '')
        os.environ['PATH'] = dll_dir + os.pathsep + old_path
        
        # Also try adding to DLL directory for Windows DLL search
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(dll_dir)
        
        try:
            ps4000 = ctypes.CDLL(dll_path)
        except OSError as e:
            raise RuntimeError(f"Failed to load DLL {dll_path}: {e}")

        # Open the device
        handle = ctypes.c_int16()
        status = ps4000.ps4000OpenUnit(ctypes.byref(handle))
        
        if status != 0:
            status_codes = {
                3: "PICO_NOT_FOUND - Device not found or PicoScope app running",
                4: "PICO_INVALID_PARAMETER",
                13: "PICO_INVALID_PARAMETER", 
                23: "PICO_USB_3_0_DEVICE_NON_USB_3_0_PORT",
                268435457: "DLL dependency issue"
            }
            error_desc = status_codes.get(status, f"Unknown status {status}")
            raise RuntimeError(f"ps4000OpenUnit failed: {error_desc} (status={status}, DLL={dll_path})")
        
        self._handle = handle
        self._lib = ps4000
        
        # Configure Channel A
        if self._channel_a_config['enabled']:
            status = ps4000.ps4000SetChannel(
                handle,
                ctypes.c_int32(0),  # Channel A
                ctypes.c_int16(1),  # enabled
                ctypes.c_int32(self._channel_a_config['coupling']),
                ctypes.c_int32(self._channel_a_config['range']),
                ctypes.c_float(self._channel_a_config['offset'])
            )
            
            if status != 0:
                ps4000.ps4000CloseUnit(handle)
                raise RuntimeError(f"ps4000SetChannel A failed with status: {status}")
        
        # Configure Channel B
        if self._channel_b_config['enabled']:
            status = ps4000.ps4000SetChannel(
                handle,
                ctypes.c_int32(1),  # Channel B
                ctypes.c_int16(1),  # enabled
                ctypes.c_int32(self._channel_b_config['coupling']),
                ctypes.c_int32(self._channel_b_config['range']),
                ctypes.c_float(self._channel_b_config['offset'])
            )
            
            if status != 0:
                ps4000.ps4000CloseUnit(handle)
                raise RuntimeError(f"ps4000SetChannel B failed with status: {status}")
        
        self._opened = True

    def _reconfigure_multi_channel_device(self) -> None:
        """Reconfigure the device for dual-channel acquisition."""
        if not self._opened or self._lib is None:
            return
        
        lib = self._lib
        handle = self._handle
        
        # Reconfigure Channel A
        if self._channel_a_config['enabled']:
            status = lib.ps4000SetChannel(
                handle,
                ctypes.c_int32(0),  # Channel A
                ctypes.c_int16(1),  # enabled
                ctypes.c_int32(self._channel_a_config['coupling']),
                ctypes.c_int32(self._channel_a_config['range']),
                ctypes.c_float(self._channel_a_config['offset'])
            )
            
            if status != 0:
                raise RuntimeError(f"ps4000SetChannel A reconfigure failed with status: {status}")
        
        # Reconfigure Channel B
        if self._channel_b_config['enabled']:
            status = lib.ps4000SetChannel(
                handle,
                ctypes.c_int32(1),  # Channel B
                ctypes.c_int16(1),  # enabled
                ctypes.c_int32(self._channel_b_config['coupling']),
                ctypes.c_int32(self._channel_b_config['range']),
                ctypes.c_float(self._channel_b_config['offset'])
            )
            
            if status != 0:
                raise RuntimeError(f"ps4000SetChannel B reconfigure failed with status: {status}")

    def _reconfigure_device(self) -> None:
        """Reconfigure the device with new settings."""
        if not self._opened or self._lib is None:
            return
        
        lib = self._lib
        handle = self._handle
        
        # Reconfigure Channel with new settings
        status = lib.ps4000SetChannel(
            handle,
            ctypes.c_int32(self._channel),
            ctypes.c_int16(1),  # enabled
            ctypes.c_int32(self._coupling),
            ctypes.c_int32(self._range),
            ctypes.c_float(0.0)  # analogue_offset - try 0.0 first
        )
        
        if status != 0:
            raise RuntimeError(f"ps4000SetChannel reconfigure failed with status: {status}")

    def _capture_block(self) -> None:
        """Capture block using proven smoke test approach."""
        lib = self._lib
        handle = self._handle
        assert lib is not None

        # Parameters - use adaptive block size for high sample rates
        # At high sample rates, we need larger blocks to keep up with data rate
        no_of_samples = 100  # Balanced block size for responsiveness and throughput
        oversample = 1
        timebase = 8  # Use fixed timebase 8 like smoke test
        
        # Get actual timing info (like smoke test)
        time_interval_ns = ctypes.c_int32()
        time_units = ctypes.c_int32()
        max_samples = ctypes.c_int32()
        
        status = lib.ps4000GetTimebase2(
            handle,
            ctypes.c_uint32(timebase),
            ctypes.c_int32(no_of_samples),
            ctypes.byref(time_interval_ns),
            ctypes.c_int16(oversample),
            ctypes.byref(max_samples),
            ctypes.c_int32(0)  # segment_index
        )
        
        if status != 0:
            raise RuntimeError(f"ps4000GetTimebase2 failed with status: {status} (timebase={timebase})")
        
        # Store actual sample interval (like smoke test)
        self._actual_sample_interval_s = time_interval_ns.value / 1e9  # Convert ns to seconds
        
        # Set up data buffer
        buffer_length = no_of_samples
        buffer = (ctypes.c_int16 * buffer_length)()
        
        status = lib.ps4000SetDataBuffer(
            handle,
            ctypes.c_int32(self._channel),
            ctypes.cast(buffer, ctypes.POINTER(ctypes.c_int16)),
            ctypes.c_int32(buffer_length),
            ctypes.c_int32(0)  # segment_index
        )
        
        if status != 0:
            raise RuntimeError(f"ps4000SetDataBuffer failed with status: {status}")
        
        # Run block capture (same as smoke test)
        pre_trigger_samples = 0
        post_trigger_samples = no_of_samples
        time_indisposed_ms = ctypes.c_int32()
        
        status = lib.ps4000RunBlock(
            self._handle,
            ctypes.c_int32(pre_trigger_samples),
            ctypes.c_int32(post_trigger_samples),
            ctypes.c_uint32(timebase),
            ctypes.c_int16(oversample),
            ctypes.byref(time_indisposed_ms),
            ctypes.c_int32(0),  # segment_index
            None,  # lpReady callback
            None   # pParameter
        )
        
        if status != 0:
            raise RuntimeError(f"ps4000RunBlock failed with status: {status}")
        
        # Wait for capture (same as smoke test)
        ready = ctypes.c_int16()
        max_wait_time = 5.0
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status = lib.ps4000IsReady(self._handle, ctypes.byref(ready))
            if status != 0:
                raise RuntimeError(f"ps4000IsReady failed with status: {status}")
            
            if ready.value:
                break
            
            time.sleep(0.01)
        
        if not ready.value:
            raise RuntimeError("Capture timed out")
        
        # Get data (same as smoke test)
        start_index = ctypes.c_uint32(0)
        no_of_samples_collected = ctypes.c_uint32(no_of_samples)
        downsampling_ratio = ctypes.c_uint32(1)
        downsampling_mode = ctypes.c_int32(0)
        segment_index = ctypes.c_uint32(0)
        overflow = ctypes.c_int16()
        
        status = lib.ps4000GetValues(
            self._handle,
            start_index,
            ctypes.byref(no_of_samples_collected),
            downsampling_ratio,
            downsampling_mode,
            segment_index,
            ctypes.byref(overflow)
        )
        
        if status != 0:
            raise RuntimeError(f"ps4000GetValues failed with status: {status}")
        
        # Check for buffer overflow
        if overflow.value != 0:
            pass  # Buffer overflow detected but continue
        
        # Validate we got the expected number of samples
        samples_retrieved = no_of_samples_collected.value
        if samples_retrieved == 0:
            raise RuntimeError("No samples retrieved from device")
        
        if samples_retrieved != no_of_samples:
            pass  # Sample count mismatch but continue
        
        # Convert to volts using range-specific formulas discovered in testing
        raw_data = np.array([buffer[i] for i in range(samples_retrieved)], dtype=np.int16)
        
        # Use the mathematically correct voltage conversion formula
        voltage_data = self._voltage_converter.convert_adc_to_voltage(raw_data, self._range)
        
        self._buf = voltage_data
        self._buf_idx = 0
        # Store the base timestamp for this buffer - use the current sample count
        # This ensures each buffer starts where the previous one ended
        self._buffer_start_sample = self._sample_count

    def _capture_dual_channel_block(self) -> None:
        """Capture dual-channel block using proven smoke test approach."""
        lib = self._lib
        handle = self._handle
        assert lib is not None

        # Parameters - use adaptive block size for high sample rates
        no_of_samples = 100  # Balanced block size for responsiveness and throughput
        oversample = 1
        timebase = 8  # Use fixed timebase 8 like smoke test
        
        # Get actual timing info (like smoke test)
        time_interval_ns = ctypes.c_int32()
        time_units = ctypes.c_int32()
        max_samples = ctypes.c_int32()
        
        status = lib.ps4000GetTimebase2(
            handle,
            ctypes.c_uint32(timebase),
            ctypes.c_int32(no_of_samples),
            ctypes.byref(time_interval_ns),
            ctypes.c_int16(oversample),
            ctypes.byref(max_samples),
            ctypes.c_int32(0)  # segment_index
        )
        
        if status != 0:
            raise RuntimeError(f"ps4000GetTimebase2 failed with status: {status} (timebase={timebase})")
        
        # Store actual sample interval (like smoke test)
        self._actual_sample_interval_s = time_interval_ns.value / 1e9  # Convert ns to seconds
        
        # Set up data buffers for both channels
        buffer_length = no_of_samples
        buffer_a = (ctypes.c_int16 * buffer_length)()
        buffer_b = (ctypes.c_int16 * buffer_length)()
        
        # Set up data buffer for Channel A
        if self._channel_a_config['enabled']:
            status = lib.ps4000SetDataBuffer(
                handle,
                ctypes.c_int32(0),  # Channel A
                ctypes.cast(buffer_a, ctypes.POINTER(ctypes.c_int16)),
                ctypes.c_int32(buffer_length),
                ctypes.c_int32(0)  # segment_index
            )
            
            if status != 0:
                raise RuntimeError(f"ps4000SetDataBuffer A failed with status: {status}")
        
        # Set up data buffer for Channel B
        if self._channel_b_config['enabled']:
            status = lib.ps4000SetDataBuffer(
                handle,
                ctypes.c_int32(1),  # Channel B
                ctypes.cast(buffer_b, ctypes.POINTER(ctypes.c_int16)),
                ctypes.c_int32(buffer_length),
                ctypes.c_int32(0)  # segment_index
            )
            
            if status != 0:
                raise RuntimeError(f"ps4000SetDataBuffer B failed with status: {status}")
        
        # Run block capture (same as smoke test)
        pre_trigger_samples = 0
        post_trigger_samples = no_of_samples
        time_indisposed_ms = ctypes.c_int32()
        
        status = lib.ps4000RunBlock(
            self._handle,
            ctypes.c_int32(pre_trigger_samples),
            ctypes.c_int32(post_trigger_samples),
            ctypes.c_uint32(timebase),
            ctypes.c_int16(oversample),
            ctypes.byref(time_indisposed_ms),
            ctypes.c_int32(0),  # segment_index
            None,  # lpReady callback
            None   # pParameter
        )
        
        if status != 0:
            raise RuntimeError(f"ps4000RunBlock failed with status: {status}")
        
        # Wait for capture (same as smoke test)
        ready = ctypes.c_int16()
        max_wait_time = 5.0
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status = lib.ps4000IsReady(self._handle, ctypes.byref(ready))
            if status != 0:
                raise RuntimeError(f"ps4000IsReady failed with status: {status}")
            
            if ready.value:
                break
            
            time.sleep(0.01)
        
        if not ready.value:
            raise RuntimeError("Capture timed out")
        
        # Get data (same as smoke test)
        start_index = ctypes.c_uint32(0)
        no_of_samples_collected = ctypes.c_uint32(no_of_samples)
        downsampling_ratio = ctypes.c_uint32(1)
        downsampling_mode = ctypes.c_int32(0)
        segment_index = ctypes.c_uint32(0)
        overflow = ctypes.c_int16()
        
        status = lib.ps4000GetValues(
            self._handle,
            start_index,
            ctypes.byref(no_of_samples_collected),
            downsampling_ratio,
            downsampling_mode,
            segment_index,
            ctypes.byref(overflow)
        )
        
        if status != 0:
            raise RuntimeError(f"ps4000GetValues failed with status: {status}")
        
        # Check for buffer overflow
        if overflow.value != 0:
            pass  # Buffer overflow detected but continue
        
        # Validate we got the expected number of samples
        samples_retrieved = no_of_samples_collected.value
        if samples_retrieved == 0:
            raise RuntimeError("No samples retrieved from device")
        
        if samples_retrieved != no_of_samples:
            pass  # Sample count mismatch but continue
        
        # Convert to volts using range-specific formulas for both channels
        raw_data_a = np.array([buffer_a[i] for i in range(samples_retrieved)], dtype=np.int16)
        raw_data_b = np.array([buffer_b[i] for i in range(samples_retrieved)], dtype=np.int16)
        
        # Use the mathematically correct voltage conversion formula for both channels
        voltage_data_a = self._voltage_converter.convert_adc_to_voltage(raw_data_a, self._channel_a_config['range'])
        voltage_data_b = self._voltage_converter.convert_adc_to_voltage(raw_data_b, self._channel_b_config['range'])
        
        self._dual_channel_buf = (voltage_data_a, voltage_data_b)
        self._dual_channel_buf_idx = 0
        # Store the base timestamp for this buffer - use the current sample count
        # This ensures each buffer starts where the previous one ended
        self._buffer_start_sample = self._sample_count


    def get_voltage_range_info(self, range_index: int) -> dict:
        """
        Get voltage range information using the new voltage converter.
        
        Args:
            range_index: The PicoScope voltage range index (0-9)
            
        Returns:
            Dictionary containing range information
        """
        return self._voltage_converter.get_conversion_info(range_index)
    
    def get_available_voltage_ranges(self) -> dict:
        """
        Get all available voltage ranges.
        
        Returns:
            Dictionary mapping range indices to VoltageRange objects
        """
        return self._voltage_converter.get_available_ranges()

    def reset_session(self) -> None:
        """Reset all session-related state for a fresh start."""
        self._start_time = None
        self._sample_count = 0
        self._buffer_start_sample = 0
        self._buf = None
        self._buf_idx = 0
        self._dual_channel_buf = None
        self._dual_channel_buf_idx = 0

    def is_multi_channel_mode(self) -> bool:
        """Check if the source is in multi-channel mode."""
        return self._multi_channel_mode

    def get_channel_config(self, channel: int) -> dict:
        """Get configuration for a specific channel."""
        if channel == 0:
            return self._channel_a_config.copy()
        elif channel == 1:
            return self._channel_b_config.copy()
        else:
            raise ValueError(f"Invalid channel: {channel}. Valid channels: 0 (A), 1 (B)")

    def set_channel_config(self, channel: int, config: dict) -> None:
        """Set configuration for a specific channel."""
        if channel == 0:
            self._channel_a_config.update(config)
        elif channel == 1:
            self._channel_b_config.update(config)
        else:
            raise ValueError(f"Invalid channel: {channel}. Valid channels: 0 (A), 1 (B)")
        
        # Reconfigure device if it's open
        if self._opened and self._lib is not None and self._multi_channel_mode:
            self._reconfigure_multi_channel_device()

    def close(self) -> None:
        if self._opened and self._lib is not None:
            try:
                self._lib.ps4000Stop(self._handle)
            except Exception:
                pass
            try:
                self._lib.ps4000CloseUnit(self._handle)
            except Exception:
                pass
        self._opened = False
        # Reset timing counters
        self._start_time = None
        self._sample_count = 0
        self._buffer_start_sample = 0

    def get_diagnostics(self) -> str:
        return f"DLL: {self._dll_path}, Handle: {self._handle.value if self._opened else 'closed'}"

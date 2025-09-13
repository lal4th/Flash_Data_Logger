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
        self._ensure_open()

    def read(self) -> Tuple[float, float]:
        self._ensure_open()
        if self._buf is None or self._buf_idx >= len(self._buf):
            try:
                self._capture_block()
            except Exception as e:
                print(f"Capture block error: {e}")
                return 0.0, 0.0
        if self._buf is None or len(self._buf) == 0:
            return 0.0, 0.0
        
        # Initialize start time on first read
        if self._start_time is None:
            self._start_time = time.perf_counter()
        
        value = float(self._buf[self._buf_idx])
        
        # Calculate proper timestamp: buffer start + position within buffer
        current_sample_number = self._buffer_start_sample + self._buf_idx
        timestamp = current_sample_number * self._actual_sample_interval_s
        
        self._buf_idx += 1
        
        # Only increment global sample count when we finish this buffer
        if self._buf_idx >= len(self._buf):
            self._sample_count = current_sample_number + 1
        
        return value, timestamp

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
            ctypes.c_float(0.0)  # analogue_offset
        )
        
        if status != 0:
            ps4000.ps4000CloseUnit(handle)
            raise RuntimeError(f"ps4000SetChannel failed with status: {status}")
        
        self._opened = True

    def _capture_block(self) -> None:
        """Capture block with smart timebase selection and proper voltage conversion."""
        lib = self._lib
        handle = self._handle
        assert lib is not None

        # Parameters
        no_of_samples = 1000
        oversample = 1
        
        # Smart timebase selection - find the best timebase for our target sample rate
        # ps4000 timebase relationship: timebase 0=1ns, 1=2ns, 2=4ns, 3=8ns, etc.
        # For timebase >= 3: time_interval = (timebase - 2) * 8ns
        target_interval_ns = int(1e9 / self._sample_rate_hz)  # Convert Hz to nanoseconds
        
        # Find appropriate timebase
        timebase = self._find_best_timebase(target_interval_ns, no_of_samples)
        
        # Get actual timing info
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
        
        # Calculate and store actual sample interval achieved
        actual_interval_ns = time_interval_ns.value
        
        # Validate the returned interval - it should be reasonable for the timebase
        # For timebase 3: expected ~8ns, for timebase 8: expected ~48ns, etc.
        expected_interval_ns = self._calculate_expected_interval_ns(timebase)
        is_reasonable = (actual_interval_ns > 0 and 
                        actual_interval_ns >= expected_interval_ns * 0.1 and 
                        actual_interval_ns <= expected_interval_ns * 10.0)
        
        if is_reasonable:
            self._actual_sample_interval_s = actual_interval_ns / 1e9  # Convert ns to seconds
            actual_sample_rate = int(1e9 / actual_interval_ns)
        else:
            # ps4000GetTimebase2 returned unreasonable value, use direct calculation
            # For ps4000: timebase 3 = 8ns, 4 = 16ns, 5 = 32ns, etc.
            calculated_interval_ns = expected_interval_ns
            
            self._actual_sample_interval_s = calculated_interval_ns / 1e9
            actual_sample_rate = int(1e9 / calculated_interval_ns)
        
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
            print(f"Warning: Buffer overflow detected (overflow={overflow.value})")
        
        # Validate we got the expected number of samples
        samples_retrieved = no_of_samples_collected.value
        if samples_retrieved == 0:
            raise RuntimeError("No samples retrieved from device")
        
        if samples_retrieved != no_of_samples:
            print(f"Warning: Expected {no_of_samples} samples, got {samples_retrieved}")
        
        # Convert to volts using proper range mapping
        max_adc = 32767
        voltage_range_v = self._get_voltage_range_volts(self._range)
        
        raw_data = np.array([buffer[i] for i in range(samples_retrieved)], dtype=np.int16)
        voltage_data = (raw_data.astype(np.float64) * voltage_range_v) / max_adc
        
        self._buf = voltage_data
        self._buf_idx = 0
        # Store the base timestamp for this buffer
        self._buffer_start_sample = self._sample_count

    def _calculate_expected_interval_ns(self, timebase: int) -> int:
        """Calculate expected interval in nanoseconds for a given timebase."""
        # ps4000 timebase to interval mapping:
        # timebase 0: 1 ns, 1: 2 ns, 2: 4 ns, 3: 8 ns
        # timebase >= 3: interval = (timebase - 2) * 8 ns
        if timebase >= 3:
            return (timebase - 2) * 8
        else:
            return 2 ** timebase  # 0=1ns, 1=2ns, 2=4ns

    def _find_best_timebase(self, target_interval_ns: int, no_of_samples: int) -> int:
        """Find the best timebase for the target sample rate."""
        lib = self._lib
        assert lib is not None
        
        # ps4000 timebase to interval mapping:
        # timebase 0: 1 ns, 1: 2 ns, 2: 4 ns, 3: 8 ns
        # timebase >= 3: interval = (timebase - 2) * 8 ns
        
        # Start with a reasonable timebase and search
        for timebase in range(3, 50):  # Start from timebase 3 (8ns)
            time_interval_ns = ctypes.c_int32()
            max_samples = ctypes.c_int32()
            
            status = lib.ps4000GetTimebase2(
                self._handle,
                ctypes.c_uint32(timebase),
                ctypes.c_int32(no_of_samples),
                ctypes.byref(time_interval_ns),
                ctypes.c_int16(1),  # oversample
                ctypes.byref(max_samples),
                ctypes.c_int32(0)  # segment_index
            )
            
            if status == 0:
                # Valid timebase found - check if it's close to our target
                actual_interval = time_interval_ns.value
                if actual_interval >= target_interval_ns * 0.5:  # Within reasonable range
                    return timebase
        
        # Fallback to our known working timebase from smoke test
        return 8

    def _get_voltage_range_volts(self, range_enum: int) -> float:
        """Convert ps4000 range enum to voltage range in volts."""
        # ps4000 voltage range mapping (from UI and documentation)
        range_map = {
            0: 0.010,   # ±10 mV
            1: 0.020,   # ±20 mV  
            2: 0.050,   # ±50 mV
            3: 0.100,   # ±100 mV
            4: 0.200,   # ±200 mV
            5: 0.500,   # ±500 mV
            6: 1.0,     # ±1 V
            7: 5.0,     # ±5 V
            8: 10.0,    # ±10 V
            9: 20.0,    # ±20 V
        }
        return range_map.get(range_enum, 5.0)  # Default to ±5V

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

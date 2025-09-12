from __future__ import annotations

import ctypes
import os
import time
from typing import Tuple, Optional

import numpy as np

from app.acquisition.source import AcquisitionSource


class PicoPs4000Source(AcquisitionSource):
    """Reliable ps4000 block-mode reader based on proven smoke test implementation.

    This implementation captures small blocks and streams them sample-by-sample.
    """

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

    # ---- AcquisitionSource ----
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
        self._ensure_open()

    def read(self) -> Tuple[float, float]:
        self._ensure_open()
        if self._buf is None or self._buf_idx >= len(self._buf):
            self._capture_block()
        if self._buf is None or len(self._buf) == 0:
            return 0.0, time.perf_counter()
        value = float(self._buf[self._buf_idx])
        self._buf_idx += 1
        return value, time.perf_counter()

    # ---- Internals ----
    def _find_ps4000_dll(self) -> str:
        """Locate ps4000.dll by scanning common PicoSDK installation paths."""
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
        
        raise RuntimeError(f"{dll_name} not found in any search paths: {search_paths}")

    def _ensure_open(self) -> None:
        if self._opened:
            return

        # Find the DLL
        dll_path = self._find_ps4000_dll()
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
            # Common status codes for better diagnostics
            status_codes = {
                3: "PICO_NOT_FOUND - Device not found or PicoScope app running",
                4: "PICO_INVALID_PARAMETER",
                13: "PICO_INVALID_PARAMETER", 
                23: "PICO_USB_3_0_DEVICE_NON_USB_3_0_PORT",
                268435457: "DLL dependency issue - picoipp.dll may be missing"
            }
            error_desc = status_codes.get(status, f"Unknown status {status}")
            raise RuntimeError(f"ps4000OpenUnit failed: {error_desc} (status={status}, DLL={dll_path})")
        
        self._handle = handle
        
        # Configure Channel A
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
        self._lib = ps4000

    def _capture_block(self) -> None:
        """Capture a block of samples using the proven approach from smoke test."""
        lib = self._lib
        assert lib is not None

        # Use proven parameters from smoke test
        no_of_samples = 1000
        timebase = 8  # Known working timebase from smoke test
        oversample = 1
        
        # Find valid timebase
        time_interval_ns = ctypes.c_int32()
        time_units = ctypes.c_int32()
        max_samples = ctypes.c_int32()
        
        status = lib.ps4000GetTimebase2(
            self._handle,
            ctypes.c_uint32(timebase),
            ctypes.c_int32(no_of_samples),
            ctypes.byref(time_interval_ns),
            ctypes.c_int16(oversample),
            ctypes.byref(max_samples),
            ctypes.c_int32(0)  # segment_index
        )
        
        if status != 0:
            raise RuntimeError(f"ps4000GetTimebase2 failed with status: {status}")
        
        # Set up data buffer
        buffer_length = no_of_samples
        buffer = (ctypes.c_int16 * buffer_length)()
        
        status = lib.ps4000SetDataBuffer(
            self._handle,
            ctypes.c_int32(self._channel),
            ctypes.cast(buffer, ctypes.POINTER(ctypes.c_int16)),
            ctypes.c_int32(buffer_length),
            ctypes.c_int32(0)  # segment_index
        )
        
        if status != 0:
            raise RuntimeError(f"ps4000SetDataBuffer failed with status: {status}")
        
        # Run block capture
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
        
        # Wait for capture to complete
        ready = ctypes.c_int16()
        max_wait_time = 5.0  # seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status = lib.ps4000IsReady(self._handle, ctypes.byref(ready))
            if status != 0:
                raise RuntimeError(f"ps4000IsReady failed with status: {status}")
            
            if ready.value:
                break
            
            time.sleep(0.01)  # 10ms poll
        
        if not ready.value:
            raise RuntimeError("Capture timed out")
        
        # Get the data
        start_index = ctypes.c_uint32(0)
        no_of_samples_collected = ctypes.c_uint32(no_of_samples)
        downsampling_ratio = ctypes.c_uint32(1)
        downsampling_mode = ctypes.c_int32(0)  # PS4000_RATIO_MODE_NONE
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
        
        # Convert ADC counts to volts and store in buffer
        max_adc = 32767  # 16-bit ADC
        voltage_range_v = 5.0  # ±5V range (we'll use the configured range later)
        
        # Convert to numpy array for easier processing
        raw_data = np.array([buffer[i] for i in range(no_of_samples_collected.value)], dtype=np.int16)
        
        # Convert to volts
        voltage_data = (raw_data.astype(np.float64) * voltage_range_v) / max_adc
        
        self._buf = voltage_data
        self._buf_idx = 0

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

    def get_diagnostics(self) -> str:
        """Return diagnostic information for debugging."""
        return f"DLL: {self._dll_path}, Handle: {self._handle.value if self._opened else 'closed'}"



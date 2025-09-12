from __future__ import annotations

import threading
import time
from ctypes import (
    POINTER,
    WINFUNCTYPE,
    WinDLL,
    byref,
    c_int16,
    c_int32,
    c_uint32,
    c_void_p,
)
from typing import Optional, Tuple

import numpy as np

from app.acquisition.source import AcquisitionSource
from app.acquisition.pico import _add_windows_dll_dirs, _preload_sdk_dlls


class PicoPs4000StreamingSource(AcquisitionSource):
    """ps4000 streaming-mode source using ps4000GetStreamingLatestValues.

    - Single channel (default A), DC coupling, +/-5 V by default
    - Converts ADC counts to volts
    - Maintains a ring buffer and yields one sample per read()
    """

    def __init__(self) -> None:
        self._sample_rate_hz: int = 100
        self._channel: int = 0
        self._coupling: int = 1
        self._range: int = 7

        self._handle = c_int16(0)
        self._lib: Optional[WinDLL] = None
        self._opened = False

        self._buf_ring: np.ndarray = np.empty(0, dtype=np.float64)
        self._buf_idx_read = 0
        self._buf_idx_write = 0
        self._buf_capacity = 0

        self._lock = threading.Lock()
        self._stream_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._effective_rate_hz: float = 0.0
        self._lsb_to_volts: float = 1.0 / 32767.0
        self._overview_buf: Optional[np.ndarray] = None
        self._overview_ptr = None
        self._cb = None

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
        new_rate = max(1, int(sample_rate_hz))
        channel = int(channel)
        coupling = int(coupling)
        v_range = int(voltage_range)
        rate_changed = self._opened and new_rate != self._sample_rate_hz
        chan_changed = self._opened and (channel != self._channel or coupling != self._coupling or v_range != self._range)
        self._sample_rate_hz = new_rate
        self._channel = channel
        self._coupling = coupling
        self._range = v_range
        if self._opened and (rate_changed or chan_changed):
            self._stop_streaming()
        self._ensure_streaming()

    def read(self) -> Tuple[float, float]:
        self._ensure_streaming()
        # If no data available, sleep briefly and return 0
        for _ in range(3):
            with self._lock:
                if self._buf_capacity > 0 and self._buf_idx_read != self._buf_idx_write:
                    value = float(self._buf_ring[self._buf_idx_read])
                    self._buf_idx_read = (self._buf_idx_read + 1) % self._buf_capacity
                    return value, time.perf_counter()
            time.sleep(0.001)
        return 0.0, time.perf_counter()

    def close(self) -> None:
        self._stop_streaming()

    def get_effective_sample_rate_hz(self) -> float:
        return float(self._effective_rate_hz)

    # ---- Internals ----
    def _ensure_streaming(self) -> None:
        if self._opened:
            return
        _add_windows_dll_dirs()
        _preload_sdk_dlls()

        import os
        from pathlib import Path

        candidates = [
            Path(os.environ.get("PROGRAMFILES", r"C:\\Program Files"))
            / "Pico Technology"
            / "SDK"
            / "lib"
            / "ps4000.dll",
            Path(os.environ.get("PROGRAMFILES", r"C:\\Program Files"))
            / "Pico Technology"
            / "PicoScope 7 T&M Stable"
            / "ps4000.dll",
        ]
        dll_path = None
        for p in candidates:
            if p.exists():
                dll_path = str(p)
                break
        if dll_path is None:
            raise RuntimeError("ps4000.dll not found for streaming")

        lib = WinDLL(dll_path)
        self._lib = lib

        # Signatures used
        lib.ps4000OpenUnit.argtypes = [POINTER(c_int16)]
        lib.ps4000OpenUnit.restype = c_int16
        lib.ps4000CloseUnit.argtypes = [c_int16]
        lib.ps4000CloseUnit.restype = c_int16
        lib.ps4000Stop.argtypes = [c_int16]
        lib.ps4000Stop.restype = c_int16
        lib.ps4000SetChannel.argtypes = [c_int16, c_int32, c_int16, c_int16, c_int32]
        lib.ps4000SetChannel.restype = c_int16
        lib.ps4000SetDataBuffer.argtypes = [c_int16, c_int32, POINTER(c_int16), c_int32]
        lib.ps4000SetDataBuffer.restype = c_int16
        # Callback signature: (handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, pParam)
        STREAMING_READY = WINFUNCTYPE(
            None, c_int16, c_int32, c_uint32, c_int16, c_uint32, c_int16, c_int16, c_void_p
        )
        lib.ps4000GetStreamingLatestValues.argtypes = [c_int16, STREAMING_READY, c_void_p]
        lib.ps4000GetStreamingLatestValues.restype = c_int16
        lib.ps4000RunStreaming.argtypes = [
            c_int16,
            POINTER(c_uint32),  # sampleInterval
            c_int32,  # timeUnits (enum)
            c_uint32,  # maxPreTriggerSamples
            c_uint32,  # maxPostTriggerSamples
            c_int16,  # autoStop
            c_uint32,  # downSampleRatio
            c_int32,  # downSampleRatioMode (enum)
            c_uint32,  # overviewBufferSize
        ]
        lib.ps4000RunStreaming.restype = c_int16

        # Open
        status = lib.ps4000OpenUnit(byref(self._handle))
        if status != 0:
            raise RuntimeError(f"ps4000OpenUnit failed: {status}")

        # Configure channel
        st = lib.ps4000SetChannel(self._handle, c_int32(self._channel), c_int16(1), c_int16(self._coupling), c_int32(self._range))
        if st != 0:
            lib.ps4000CloseUnit(self._handle)
            raise RuntimeError(f"ps4000SetChannel failed: {st}")

        # Voltage scaling per selected input range (full-scale volts)
        full_scale_by_range = {
            0: 0.01,
            1: 0.02,
            2: 0.05,
            3: 0.1,
            4: 0.2,
            5: 0.5,
            6: 1.0,
            7: 5.0,
            8: 10.0,
            9: 20.0,
        }
        self._lsb_to_volts = float(full_scale_by_range.get(self._range, 5.0)) / 32767.0

        # Allocate a ring buffer for a few seconds of data
        seconds = 5
        capacity = max(1024, int(self._sample_rate_hz * seconds))
        self._buf_ring = np.zeros(capacity, dtype=np.float64)
        self._buf_capacity = capacity
        self._buf_idx_read = 0
        self._buf_idx_write = 0

        # Allocate overview buffer used by driver for this channel and register once
        self._overview_buf = np.zeros(capacity, dtype=np.int16)
        self._overview_ptr = self._overview_buf.ctypes.data_as(POINTER(c_int16))
        st = lib.ps4000SetDataBuffer(self._handle, c_int32(self._channel), self._overview_ptr, c_int32(capacity))
        if st != 0:
            lib.ps4000CloseUnit(self._handle)
            raise RuntimeError(f"ps4000SetDataBuffer failed: {st}")

        # Start streaming
        # timeUnits enum for ps4000: 0=fs,1=ps,2=ns,3=us,4=ms,5=s (use microseconds)
        interval_us = max(1, int(round(1_000_000 / float(self._sample_rate_hz))))
        sampleInterval = c_uint32(interval_us)
        timeUnits = c_int32(3)  # microseconds
        maxPre = c_uint32(0)
        maxPost = c_uint32(0)  # 0 for continuous streaming
        autoStop = c_int16(0)
        downSampleRatio = c_uint32(1)
        downSampleMode = c_int32(0)  # none
        overviewBufferSize = c_uint32(capacity)
        st = lib.ps4000RunStreaming(
            self._handle,
            byref(sampleInterval),
            timeUnits,
            maxPre,
            maxPost,
            autoStop,
            downSampleRatio,
            downSampleMode,
            overviewBufferSize,
        )
        if st != 0:
            lib.ps4000CloseUnit(self._handle)
            raise RuntimeError(f"ps4000RunStreaming failed: {st}")
        # Driver may adjust the interval; capture effective rate
        try:
            actual_us = int(sampleInterval.value)
            if actual_us <= 0:
                actual_us = interval_us
        except Exception:
            actual_us = interval_us
        self._effective_rate_hz = 1_000_000.0 / float(actual_us)

        # Background thread to poll for latest values
        self._stop_event.clear()
        # Create and retain callback so it isn't GC'd
        def _on_stream_ready(handle: c_int16, noOfSamples: c_int32, startIndex: c_uint32, overflow: c_int16, triggerAt: c_uint32, triggered: c_int16, autoStopFlag: c_int16, pParam: c_void_p) -> None:  # noqa: E501
            try:
                buf = self._overview_buf
                if buf is None:
                    return
                n = int(noOfSamples)
                if n <= 0:
                    return
                start = int(startIndex)
                end = start + n
                # Wrap-around handling
                if end <= buf.size:
                    chunk = buf[start:end]
                else:
                    part1 = buf[start:]
                    part2 = buf[: end % buf.size]
                    chunk = np.concatenate((part1, part2))
                # Scale to volts and push to ring
                data = chunk.astype(np.float64) * self._lsb_to_volts
                with self._lock:
                    for v in data:
                        self._buf_ring[self._buf_idx_write] = float(v)
                        self._buf_idx_write = (self._buf_idx_write + 1) % self._buf_capacity
                        if self._buf_idx_write == self._buf_idx_read:
                            self._buf_idx_read = (self._buf_idx_read + 1) % self._buf_capacity
            except Exception:
                pass

        self._cb = STREAMING_READY(_on_stream_ready)

        self._stream_thread = threading.Thread(target=self._poll_stream, daemon=True)
        self._stream_thread.start()
        self._opened = True

    def _poll_stream(self) -> None:
        assert self._lib is not None
        lib = self._lib

        while not self._stop_event.is_set():
            try:
                lib.ps4000GetStreamingLatestValues(self._handle, self._cb, None)
                time.sleep(max(0.0, 1.0 / 60.0))
            except Exception:
                time.sleep(0.01)

    def _stop_streaming(self) -> None:
        if self._lib is None:
            return
        self._stop_event.set()
        if self._stream_thread and self._stream_thread.is_alive():
            self._stream_thread.join(timeout=1)
        try:
            self._lib.ps4000Stop(self._handle)
        except Exception:
            pass
        try:
            self._lib.ps4000CloseUnit(self._handle)
        except Exception:
            pass
        self._opened = False



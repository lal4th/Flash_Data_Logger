from __future__ import annotations

import math
import time
from abc import ABC, abstractmethod
from typing import Tuple, Optional


class AcquisitionSource(ABC):
    @abstractmethod
    def configure(
        self,
        *,
        sample_rate_hz: int,
        channel: int = 0,
        coupling: int = 1,
        voltage_range: int = 7,
        resolution_bits: int = 16,
    ) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    @abstractmethod
    def read(self) -> Tuple[float, float]:  # returns (value, timestamp)
        raise NotImplementedError

    def close(self) -> None:
        """Optional cleanup hook for concrete sources."""
        return None


class DummySineSource(AcquisitionSource):
    def __init__(self) -> None:
        self._sample_rate_hz = 100
        self._t0 = time.perf_counter()

    def configure(
        self,
        *,
        sample_rate_hz: int,
        channel: int = 0,
        coupling: int = 1,
        voltage_range: int = 7,
        resolution_bits: int = 16,
    ) -> None:
        self._sample_rate_hz = sample_rate_hz
        self._t0 = time.perf_counter()

    def read(self) -> Tuple[float, float]:
        now = time.perf_counter()
        t = now - self._t0
        # 2 Hz sine with small noise
        value = math.sin(2.0 * math.pi * 2.0 * t) + 0.05 * math.sin(2.0 * math.pi * 50.0 * t)
        return value, now


class DeviceDetectionResult:
    def __init__(self, api: Optional[str], model: Optional[str]):
        self.api = api
        self.model = model




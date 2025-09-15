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




class DeviceDetectionResult:
    def __init__(self, api: Optional[str], model: Optional[str]):
        self.api = api
        self.model = model




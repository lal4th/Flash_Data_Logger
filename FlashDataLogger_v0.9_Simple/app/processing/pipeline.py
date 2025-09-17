from __future__ import annotations

from collections import deque
from typing import Deque


class ProcessingPipeline:
    def __init__(self) -> None:
        # Simple moving average to smooth noise
        self._window_size = 5
        self._window: Deque[float] = deque(maxlen=self._window_size)

    def process(self, value: float) -> float:
        self._window.append(value)
        return sum(self._window) / float(len(self._window))



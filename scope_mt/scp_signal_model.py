# scp_signal_model.py
from collections import deque
from typing import Callable, Deque


ObserverFn = Callable[[], None]


class scpSignalModel:
    """
    Model owns:
      - circular buffer of processed samples
      - current config parameters (scale/offset)
      - observers for view updates
    """

    def __init__(self, max_points: int = 2000) -> None:
        self._max_points = max_points
        self._t: Deque[float] = deque(maxlen=max_points)
        self._y: Deque[float] = deque(maxlen=max_points)

        self.scale: float = 1.0
        self.offset: float = 0.0

        self._observers: list[ObserverFn] = []

    def add_observer(self, fn: ObserverFn) -> None:
        self._observers.append(fn)

    def notify(self) -> None:
        for fn in list(self._observers):
            try:
                fn()
            except Exception:
                # keep model robust if a view callback fails
                pass

    def clear(self) -> None:
        self._t.clear()
        self._y.clear()
        self.notify()

    def append_processed(self, t: float, y: float) -> None:
        self._t.append(t)
        self._y.append(y)

    def get_series(self) -> tuple[list[float], list[float]]:
        return list(self._t), list(self._y)

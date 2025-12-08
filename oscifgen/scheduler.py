# oscifgen/scheduler.py
from __future__ import annotations
import time

class Pacer:
    """
    Simple fixed-rate pacer.
    Given a target frequency (Hz), it schedules evenly spaced ticks.
    Usage:
        p = Pacer(rate_hz)
        p.start()
        # in a loop:
        p.sleep_until_next()
    """
    def __init__(self, rate_hz: float) -> None:
        self.rate_hz = float(rate_hz)
        self._period = 0.0 if self.rate_hz <= 0 else 1.0 / self.rate_hz
        self._next = 0.0
        self._started = False

    def start(self) -> None:
        now = time.perf_counter()
        self._next = now + (self._period if self._period > 0 else 0.0)
        self._started = True

    def sleep_until_next(self) -> None:
        if not self._started or self._period <= 0:
            return
        now = time.perf_counter()
        dt = self._next - now
        if dt > 0:
            time.sleep(dt)
        # schedule next tick
        self._next += self._period
        # if we fell behind a lot, catch up by jumping to “now + period”
        if self._next - time.perf_counter() < -10 * self._period:
            self._next = time.perf_counter() + self._period

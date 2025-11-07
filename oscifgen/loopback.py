# oscifgen/loopctl.py
from dataclasses import dataclass
import threading

@dataclass
class LoopPlan:
    n_bytes: int | None    # total target bytes/samples; None = ignore
    loops: int | None      # max loop iterations/chunks; None = ignore
    chunk: int             # bytes per read/write

class StopToken:
    def __init__(self) -> None:
        self._evt = threading.Event()
    def stop(self) -> None:
        self._evt.set()
    def stopped(self) -> bool:
        return self._evt.is_set()

class LoopController:
    def __init__(self, plan: LoopPlan) -> None:
        self.plan = plan
        self._bytes = 0
        self._loops = 0
        self._lock = threading.Lock()

    def step(self, bytes_this_chunk: int) -> None:
        with self._lock:
            self._bytes += bytes_this_chunk
            self._loops += 1

    def continue_running(self) -> bool:
        with self._lock:
            ok_n = (self.plan.n_bytes is None) or (self._bytes < self.plan.n_bytes)
            ok_l = (self.plan.loops   is None) or (self._loops < self.plan.loops)
            return ok_n and ok_l

    @property
    def totals(self) -> tuple[int,int]:
        with self._lock:
            return self._bytes, self._loops

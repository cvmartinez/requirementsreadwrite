import time


class scpLoopController:
    """
    Tracks samples and timing for the acquisition loop.
    """

    def __init__(self, sample_time: float) -> None:
        self.sample_time = sample_time
        self.total_samples = 0
        self._start_time = None

    def start(self) -> None:
        self._start_time = time.perf_counter()

    def step(self) -> None:
        self.total_samples += 1

    def elapsed(self) -> float:
        if self._start_time is None:
            return 0.0
        return time.perf_counter() - self._start_time

    def effective_sample_rate(self) -> float:
        e = self.elapsed()
        if e <= 0.0:
            return 0.0
        return self.total_samples / e

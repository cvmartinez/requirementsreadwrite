import time
from typing import List, Any


class scpReader:
    """
    Implements the oscilloscope "read" behavior:
    - pulls samples from SignalSource
    - runs them through the pipeline
    - sends them to the View
    - records them in a buffer
    """

    def __init__(
        self,
        config: Any,
        source: Any,
        processor: Any,
        loop_controller: Any,
        stop_token: Any,
        view: Any,
        logger: Any,
    ) -> None:
        self._config = config
        self._source = source
        self._processor = processor
        self._loop = loop_controller
        self._stop = stop_token
        self._view = view
        self._logger = logger
        self.buffer: List[float] = []

    def run(self) -> None:
        self._logger.log(
            f"Starting acquisition: "
            f"sampleTime={self._config.sample_time * 1000:.3f} ms, "
            f"duration={self._config.duration:.3f} s, "
            f"freq={self._config.freq_hz} Hz, amp={self._config.amplitude}"
        )
        self._loop.start()

        next_deadline = time.perf_counter()
        while not self._stop.is_stopped():
            # simple timing loop for the sampling period
            now = time.perf_counter()
            if now < next_deadline:
                time.sleep(next_deadline - now)
            next_deadline += self._config.sample_time

            raw = self._source.next_sample()
            processed = self._processor.process(raw)

            self.buffer.append(processed)
            self._loop.step()
            self._view.render_sample(self._loop.total_samples, processed)

        elapsed = self._loop.elapsed()
        eff_rate = self._loop.effective_sample_rate()
        self._logger.log("Acquisition finished.")
        self._view.render_summary(self._loop.total_samples, elapsed, eff_rate)

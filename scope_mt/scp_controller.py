# scp_controller.py
import threading
import time

from scp_config import scpConfig
from scp_signal_source import scpSignalSource
from scp_signal_model import scpSignalModel


class scpController:
    """
    Controller owns:
      - current scpConfig
      - sampling thread lifecycle
      - pushes processed samples into the Model
    """

    def __init__(self, model: scpSignalModel) -> None:
        self.model = model
        self.config = scpConfig()

        self._stop_evt = threading.Event()
        self._thread: threading.Thread | None = None
        self._source = scpSignalSource(
            freq_hz=self.config.freq_hz,
            amplitude=self.config.amplitude,
            sample_time_s=self.config.sample_time_s,
        )

        self._running_lock = threading.Lock()
        self._running = False

    # -------------------------
    # Public API (called by Views)
    # -------------------------

    def set_sample_time_ms(self, ms: float) -> None:
        self.config.sample_time_s = ms / 1000.0
        self._source.set_sample_time(self.config.sample_time_s)

    def set_sample_for_s(self, seconds: float) -> None:
        self.config.sample_for_s = seconds

    def set_scale(self, gain: float) -> None:
        self.config.scale = gain
        self.model.scale = gain

    def set_offset(self, offset: float) -> None:
        self.config.offset = offset
        self.model.offset = offset

    def start(self) -> None:
        with self._running_lock:
            if self._running:
                return
            self._running = True

        self._stop_evt.clear()
        self.model.clear()

        self._thread = threading.Thread(target=self._run_sampling, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_evt.set()
        with self._running_lock:
            self._running = False

    def is_running(self) -> bool:
        with self._running_lock:
            return self._running

    # -------------------------
    # Internal sampling loop
    # -------------------------

    def _run_sampling(self) -> None:
        start_wall = time.time()
        next_tick = start_wall

        while not self._stop_evt.is_set():
            elapsed = time.time() - start_wall
            if elapsed >= self.config.sample_for_s:
                break

            # pace loop by sample_time_s
            now = time.time()
            if now < next_tick:
                time.sleep(max(0.0, next_tick - now))

            # acquire raw sample from source
            t, raw = self._source.next_sample()

            # process (scale + offset)
            y = (raw * self.config.scale) + self.config.offset

            # update model
            self.model.append_processed(t, y)

            # notify views occasionally (not every sample, to reduce overhead)
            # notify ~every 20 samples
            if len(self.model.get_series()[0]) % 20 == 0:
                self.model.notify()

            next_tick += self.config.sample_time_s

        # final notify
        self.model.notify()
        with self._running_lock:
            self._running = False

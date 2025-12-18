# scp_signal_source.py
import math


class scpSignalSource:
    def __init__(self, freq_hz: float, amplitude: float, sample_time_s: float) -> None:
        self.freq_hz = freq_hz
        self.amplitude = amplitude
        self.sample_time_s = sample_time_s
        self._t = 0.0

    def set_sample_time(self, sample_time_s: float) -> None:
        self.sample_time_s = sample_time_s

    def next_sample(self) -> tuple[float, float]:
        """Returns (t_seconds, raw_value)."""
        value = self.amplitude * math.sin(2.0 * math.pi * self.freq_hz * self._t)
        t = self._t
        self._t += self.sample_time_s
        return t, value

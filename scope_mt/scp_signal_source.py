import math


class scpSignalSource:
    """
    Internal sine-wave generator used as the oscilloscope input.
    """

    def __init__(self, freq_hz: float, amplitude: float, sample_time: float) -> None:
        self.freq_hz = freq_hz
        self.amplitude = amplitude
        self.sample_time = sample_time
        self._t = 0.0

    def next_sample(self) -> float:
        """Return the next sample in the sine wave."""
        value = self.amplitude * math.sin(2.0 * math.pi * self.freq_hz * self._t)
        self._t += self.sample_time
        return value

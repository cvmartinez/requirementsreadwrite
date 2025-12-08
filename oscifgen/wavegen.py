# oscifgen/wavegen.py
from __future__ import annotations
import math
from enum import Enum

class Wave(Enum):
    SINE = "sine"
    SQUARE = "square"
    TRIANGLE = "triangle"

class Waveform:
    """
    Simple byte-stream waveform generator.
    Produces 0..255 bytes for sine/square/triangle using a phase accumulator.
    """
    def __init__(self, kind: Wave = Wave.SINE, amp: float = 1.0):
        self.kind = kind
        # clamp amplitude to [0, 1]
        self.amp = max(0.0, min(1.0, float(amp)))
        self._phase = 0.0
        # fixed step per sample (independent of real Fo/Fs for this assignment)
        self._step = 2.0 * math.pi / 64.0  # 64 samples per cycle

    def next_bytes(self, n: int) -> bytes:
        out = bytearray()
        for _ in range(int(n)):
            if self.kind == Wave.SINE:
                val = math.sin(self._phase)
            elif self.kind == Wave.SQUARE:
                val = 1.0 if math.sin(self._phase) >= 0.0 else -1.0
            else:  # TRIANGLE
                # triangle wave from normalized phase
                t = (self._phase / (2.0 * math.pi)) % 1.0  # 0..1
                val = 4.0 * abs(t - 0.5) - 1.0  # -1..1

            self._phase += self._step
            if self._phase >= 2.0 * math.pi:
                self._phase -= 2.0 * math.pi

            # scale from [-1,1] to [0,255], apply amplitude
            scaled = (val * self.amp * 0.5) + 0.5  # 0..1
            byte = int(max(0, min(255, round(scaled * 255.0))))
            out.append(byte)

        return bytes(out)

# optional helper if you prefer strings elsewhere
def make_waveform(kind_str: str, amp: float = 1.0) -> Waveform:
    k = (kind_str or "sine").lower()
    mapping = {"sine": Wave.SINE, "square": Wave.SQUARE, "triangle": Wave.TRIANGLE}
    return Waveform(mapping.get(k, Wave.SINE), amp=amp)

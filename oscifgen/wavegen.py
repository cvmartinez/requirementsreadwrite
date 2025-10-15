from __future__ import annotations
from enum import Enum
import math

class Wave(Enum):
    SINE = 1
    SQUARE = 2
    TRIANGLE = 3

def make_wave(w: Wave, n: int, amp: float = 1.0) -> bytes:
    """Return n bytes (0..255) of the waveform."""
    amp = max(0.0, min(amp, 1.0))
    out = bytearray(n)
    for i in range(n):
        t = i / n
        if w is Wave.SINE:
            x = math.sin(2.0 * math.pi * t)
        elif w is Wave.SQUARE:
            x = 1.0 if t < 0.5 else -1.0
        else:  # TRIANGLE
            x = 4.0 * abs(t - math.floor(t + 0.5)) - 1.0
        y = max(0.0, min(1.0, 0.5 + 0.5 * amp * x))
        out[i] = int(round(y * 255.0))
    return bytes(out)

from __future__ import annotations
import time
from .device import Device
from .wavegen import Waveform
# --- Added for pacing ---
from .scheduler import Pacer
# -------------------------


class Writer:
    """Implements reqfWrite: generate and write N bytes at output frequency Fo."""

    def run(self, dev: Device, out_path: str, N: int, Fo: float, wave: Waveform) -> int:
        if N <= 0 or Fo <= 0:
            print("Invalid N or Fo")
            return 2
        if not dev.open(out_path):
            print("Open failed (output)")
            return 2

        CHUNK = 1024
        total = 0
        t0 = time.perf_counter()
        p = Pacer(Fo)
        p.start()

        while total < N:
            need = min(CHUNK, N - total)
            buf = wave.next_bytes(need)
            w = dev.write(buf)
            if w.bytes < 0 or w.err:
                print(f"Write error: {w.err}")
                break
            total += w.bytes
            p.sleep_until_next()

        dev.close()
        t1 = time.perf_counter()
        elapsed = t1 - t0
        thr = (total / elapsed) if elapsed > 0 else 0.0
        print(
            f"WRITE bytes={total} time_s={elapsed:.6f} throughput_Bps={thr:.2f}")
        return 0

from __future__ import annotations
import time
from .device import Device
from .wavegen import make_wave, Wave

class Writer:
    """Implements reqfWrite: write N bytes at output frequency Fo."""
    def run(self, dev: Device, out_path: str, N: int, Fo: float, wave: Wave, amp: float) -> int:
        if N <= 0 or Fo <= 0:
            print("Invalid N or Fo")
            return 2
        if not dev.open(out_path):
            print("Open failed (output)")
            return 2

        data = make_wave(wave, N, amp)
        CHUNK = 1024
        total = 0
        t0 = time.perf_counter()

        while total < N:
            n = min(CHUNK, N - total)
            r = dev.write(data[total: total + n])
            if r.bytes <= 0 or r.err:
                print(f"Write error: {r.err}")
                break
            total += r.bytes
            # pace to ~1/Fo
            time.sleep(max(0.0, 1.0 / Fo))

        dev.close()
        t1 = time.perf_counter()
        elapsed = t1 - t0
        thr = (total / elapsed) if elapsed > 0 else 0.0
        print(f"WRITE bytes={total} time_s={elapsed:.6f} throughput_Bps={thr:.2f}")
        return 0

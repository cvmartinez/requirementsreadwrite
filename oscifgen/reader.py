from __future__ import annotations
import time
from statistics import median
from .device import Device
from typing import List

def percentile(vals: List[float], p: float) -> float:
    if not vals:
        return 0.0
    vals = sorted(vals)
    k = (len(vals) - 1) * p
    f = int(k)
    c = min(f + 1, len(vals) - 1)
    if f == c:
        return vals[f]
    d0 = vals[f] * (c - k)
    d1 = vals[c] * (k - f)
    return d0 + d1

class Reader:
    """Implements reqfRead: read N bytes at sampling frequency Fs."""
    def run(self, dev: Device, in_path: str, N: int, Fs: float, out_path: str) -> int:
        if N <= 0 or Fs <= 0:
            print("Invalid N or Fs")
            return 2
        if not dev.open(in_path):
            print("Open failed (input)")
            return 2

        try:
            fout = open(out_path, "wb")
        except OSError:
            print("Can't open output file")
            dev.close()
            return 3

        CHUNK = 1024
        total = 0
        t0 = time.perf_counter()
        last = t0
        intervals: List[float] = []

        while total < N:
            need = min(CHUNK, N - total)
            r = dev.read(need)
            if r.bytes < 0 or r.err:
                print(f"Read error: {r.err}")
                break
            if r.bytes == 0:
                break  # EOF
            # write what we "received"
            fout.write(b'\x00' * r.bytes)  # we don't need actual data content for the mock
            total += r.bytes

            now = time.perf_counter()
            intervals.append(now - last)
            last = now

            # pace to ~1/Fs
            sleep_s = max(0.0, (1.0 / Fs))
            time.sleep(sleep_s)

        fout.close()
        dev.close()
        t1 = time.perf_counter()
        elapsed = t1 - t0
        thr = (total / elapsed) if elapsed > 0 else 0.0
        p50 = percentile(intervals, 0.50)
        p95 = percentile(intervals, 0.95)
        print(f"READ bytes={total} time_s={elapsed:.6f} throughput_Bps={thr:.2f} "
              f"latency_p50_s={p50:.6f} latency_p95_s={p95:.6f}")
        return 0

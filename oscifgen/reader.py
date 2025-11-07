from __future__ import annotations
import time
from statistics import median
from typing import List, Optional
from .device import Device

# --- pacing and metrics (unchanged) ---
from .stats import RunStats, throughput_bytes_per_s
from .scheduler import Pacer
# --------------------------------------


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
    """
    Implements reqfRead:
    Read bytes from input at sampling frequency Fs and write to output file.
    Termination is controlled by N (bytes) and/or loops (iteration count).
    If both are provided, N takes precedence (stop as soon as N is reached).
    """

    def run(
        self,
        dev: Device,
        in_path: str,
        out_path: str,
        fs: float,
        n: Optional[int] = None,
        loops: Optional[int] = None,
        chunk: int = 1024,
    ) -> int:
        # Validate termination conditions
        if (n is None and loops is None) or fs <= 0:
            print("Provide --n or --loops (or both), and a positive --fs.")
            return 2
        if n is not None and n <= 0:
            print("Invalid N (must be > 0).")
            return 2
        if loops is not None and loops <= 0:
            print("Invalid loops (must be > 0).")
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

        total_bytes = 0
        iter_count = 0
        t0 = time.perf_counter()
        rs = RunStats()           # collect latency intervals
        p = Pacer(fs)
        p.start()
        last = t0

        def need_this_iter() -> int:
            # If N is set, cap this read so we don't overshoot
            if n is None:
                return chunk
            remaining = n - total_bytes
            return chunk if remaining >= chunk else max(0, remaining)

        # Loop until N or loops condition is satisfied
        status = 0
        try:
            while True:
                # Check termination BEFORE reading if loops limit only (no N) is set
                if n is None and loops is not None and iter_count >= loops:
                    break
                # If N is set and already reached, stop
                if n is not None and total_bytes >= n:
                    break

                need = need_this_iter()
                if need == 0:
                    break  # exactly satisfied N

                r = dev.read(need)
                if r.bytes < 0 or r.err:
                    print(f"Read error: {r.err}")
                    status = 1
                    break
                if r.bytes == 0:
                    # EOF or no data
                    break


                # Write placeholder bytes (mock path). Replace with actual buffer if needed.
                fout.write(b'\x00' * r.bytes)
                total_bytes += r.bytes
                iter_count += 1

                now = time.perf_counter()
                rs.mark_interval(now - last)
                last = now
                p.sleep_until_next()
        finally:
            fout.close()
            dev.close()

        t1 = time.perf_counter()
        elapsed = max(1e-12, t1 - t0)
        thr = throughput_bytes_per_s(total_bytes, elapsed)
        print(
            f"READ bytes_total={total_bytes} loops_total={iter_count} "
            f"time_s={elapsed:.6f} throughput_Bps={thr:.2f} "
            f"latency_p50_s={rs.p50():.6f} latency_p95_s={rs.p95():.6f}"
        )
        return status


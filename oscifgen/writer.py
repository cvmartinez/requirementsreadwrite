from __future__ import annotations
import time
from typing import Optional
from .device import Device
from .wavegen import Waveform

# --- pacing (unchanged) ---
from .scheduler import Pacer
# --------------------------


class Writer:
    """
    Implements reqfWrite:
    Generate and write bytes at output frequency Fo.
    Termination is controlled by N (bytes) and/or loops (iteration count).
    If both are provided, N takes precedence (stop as soon as N is reached).
    """

    def run(
        self,
        dev: Device,
        out_path: str,
        fo: float,
        wave: Waveform,
        amp: float = 1.0,            # kept for CLI parity; apply inside wave if desired
        n: Optional[int] = None,
        loops: Optional[int] = None,
        chunk: int = 1024,
    ) -> int:
        # Validate termination conditions
        if (n is None and loops is None) or fo <= 0:
            print("Provide --n or --loops (or both), and a positive --fo.")
            return 2
        if n is not None and n <= 0:
            print("Invalid N (must be > 0).")
            return 2
        if loops is not None and loops <= 0:
            print("Invalid loops (must be > 0).")
            return 2

        if not dev.open(out_path):
            print("Open failed (output)")
            return 2

        total_bytes = 0
        iter_count = 0
        t0 = time.perf_counter()
        p = Pacer(fo)
        p.start()

        def need_this_iter() -> int:
            if n is None:
                return chunk
            remaining = n - total_bytes
            return chunk if remaining >= chunk else max(0, remaining)

        status = 0
        try:
            while True:
                # Check termination BEFORE writing if loops-only
                if n is None and loops is not None and iter_count >= loops:
                    break
                if n is not None and total_bytes >= n:
                    break

                need = need_this_iter()
                if need == 0:
                    break

                # Generate waveform bytes; apply amp scale inside your wavegen if supported.
                buf = wave.next_bytes(need)
                w = dev.write(buf)
                if w.bytes < 0 or w.err:
                    print(f"Write error: {w.err}")
                    status = 1
                    break
                total_bytes += w.bytes
                iter_count += 1
                p.sleep_until_next()
        finally:
            dev.close()

        t1 = time.perf_counter()
        elapsed = max(1e-12, t1 - t0)
        thr = (total_bytes / elapsed) if elapsed > 0 else 0.0
        print(
            f"WRITE bytes_total={total_bytes} loops_total={iter_count} "
            f"time_s={elapsed:.6f} throughput_Bps={thr:.2f}"
        )
        return status



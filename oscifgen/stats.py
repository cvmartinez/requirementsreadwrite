from __future__ import annotations
from typing import List

class RunStats:
    """Collects latency intervals and computes percentiles."""
    def __init__(self) -> None:
        self._vals: List[float] = []

    def mark_interval(self, dt: float) -> None:
        if dt >= 0:
            self._vals.append(dt)

    def _percentile(self, p: float) -> float:
        vals = sorted(self._vals)
        if not vals:
            return 0.0
        k = (len(vals) - 1) * p
        f = int(k)
        c = min(f + 1, len(vals) - 1)
        if f == c:
            return vals[f]
        d0 = vals[f] * (c - k)
        d1 = vals[c] * (k - f)
        return d0 + d1

    def p50(self) -> float: return self._percentile(0.50)
    def p95(self) -> float: return self._percentile(0.95)

def throughput_bytes_per_s(total_bytes: int, elapsed_s: float) -> float:
    if elapsed_s <= 0:
        return 0.0
    return float(total_bytes) / float(elapsed_s)

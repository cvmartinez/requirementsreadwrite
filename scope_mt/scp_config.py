# scp_config.py
from dataclasses import dataclass


@dataclass
class scpConfig:
    sample_time_s: float = 0.001  # 1ms default
    sample_for_s: float = 10.0    # 10s default
    scale: float = 1.0
    offset: float = 0.0
    freq_hz: float = 2.0
    amplitude: float = 1.0

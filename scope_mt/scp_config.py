from dataclasses import dataclass


@dataclass
class scpConfig:
    """Configuration for a scope acquisition run."""
    sample_time: float   # seconds between samples
    duration: float      # total acquisition time in seconds
    scale: float = 1.0
    offset: float = 0.0
    freq_hz: float = 2.0
    amplitude: float = 1.0

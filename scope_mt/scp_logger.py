import sys
import time
from typing import TextIO


class scpLogger:
    """Very small logger used across the app."""

    def __init__(self, stream: TextIO | None = None) -> None:
        self._stream = stream or sys.stdout

    def log(self, message: str) -> None:
        ts = time.strftime("%H:%M:%S")
        self._stream.write(f"[{ts}] {message}\n")
        self._stream.flush()

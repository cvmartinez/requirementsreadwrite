from __future__ import annotations
from abc import ABC, abstractmethod

class IoResult:
    def __init__(self, bytes_: int, err: str = ""):
        self.bytes = bytes_
        self.err = err  # empty => OK

class Device(ABC):
    @abstractmethod
    def open(self, path: str) -> bool: ...
    @abstractmethod
    def close(self) -> None: ...
    @abstractmethod
    def read(self, n: int) -> IoResult: ...
    @abstractmethod
    def write(self, data: bytes) -> IoResult: ...
    @abstractmethod
    def is_connected(self) -> bool: ...

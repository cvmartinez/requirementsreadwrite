from __future__ import annotations
from .device import Device, IoResult

class FileDevice(Device):
    """
    Convention:
      - If path ends with ".in": open file for reading (mock input stream).
      - Otherwise: open file for writing (mock output sink).
    """
    def __init__(self) -> None:
        self._in = None
        self._out = None

    def open(self, path: str) -> bool:
        if path.endswith(".in"):
            try:
                self._in = open(path, "rb")
                return True
            except OSError:
                return False
        else:
            try:
                self._out = open(path, "wb")
                return True
            except OSError:
                return False

    def close(self) -> None:
        if self._in and not self._in.closed:
            self._in.close()
        if self._out and not self._out.closed:
            self._out.close()
        self._in = None
        self._out = None

    def read(self, n: int) -> IoResult:
        if not self._in:
            return IoResult(-1, "not-open-input")
        try:
            data = self._in.read(n)
            if data is None:
                return IoResult(0, "")
            return IoResult(len(data), "")
        except OSError as e:
            return IoResult(0, f"read-error:{e}")

    def write(self, data: bytes) -> IoResult:
        if not self._out:
            return IoResult(-1, "not-open-output")
        try:
            self._out.write(data)
            self._out.flush()
            return IoResult(len(data), "")
        except OSError as e:
            return IoResult(0, f"write-error:{e}")

    def is_connected(self) -> bool:
        return (self._in and not self._in.closed) or (self._out and not self._out.closed)

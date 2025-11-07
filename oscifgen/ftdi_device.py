# ftdi_device.py
from __future__ import annotations
from pyftdi.serialext import serial_for_url
from .device import Device, IoResult


class FtdiDevice(Device):
    """
    Simple FTDI backend using pyftdi's serial URL.
    Default URL opens the first available interface 1.
    """

    def __init__(self, url: str = 'ftdi://::/1', baudrate: int = 3_000_000, timeout: float = 0.05):
        self.url = url
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None

    def open(self, path: str = '') -> bool:
        try:
            # 'path' unused; we rely on URL fields
            self.serial = serial_for_url(
                self.url, baudrate=self.baudrate, timeout=self.timeout)
            return True
        except Exception:
            return False

    def close(self) -> None:
        try:
            if self.serial:
                self.serial.close()
        finally:
            self.serial = None

    def read(self, n: int) -> IoResult:
        if not self.serial:
            return IoResult(-1, "not-open")
        try:
            data = self.serial.read(n)
            return IoResult(len(data) if data else 0, "")
        except Exception as e:
            return IoResult(0, f"read-error:{e}")

    def write(self, data: bytes) -> IoResult:
        if not self.serial:
            return IoResult(-1, "not-open")
        try:
            n = self.serial.write(data)
            self.serial.flush()
            return IoResult(int(n), "")
        except Exception as e:
            return IoResult(0, f"write-error:{e}")

    def is_connected(self) -> bool:
        return self.serial is not None

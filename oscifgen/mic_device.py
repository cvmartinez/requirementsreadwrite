# oscifgen/mic_device.py
from __future__ import annotations
from .device import Device, IoResult

import sounddevice as sd


class MicrophoneDevice(Device):
    """
    Device implementation that uses the default system microphone as the input
    source. It implements the same Device interface used by Reader/Writer.

    open(path: str) ignores the path (kept only to satisfy the interface).
    """

    def __init__(self, samplerate: int = 44100, channels: int = 1, dtype: str = "int16") -> None:
        self.samplerate = samplerate
        self.channels = channels
        self.dtype = dtype
        self._stream: sd.InputStream | None = None

    def open(self, path: str) -> bool:
        """Open the default microphone input."""
        try:
            self._stream = sd.InputStream(
                samplerate=self.samplerate,
                channels=self.channels,
                dtype=self.dtype,
            )
            self._stream.start()
            return True
        except Exception as e:
            print(f"Microphone open failed: {e}")
            self._stream = None
            return False

    def close(self) -> None:
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            finally:
                self._stream = None

    def read(self, n: int) -> IoResult:
        """
        Read approximately n bytes from the microphone.

        NOTE: Reader.py only cares about the *number* of bytes read, not the
        actual data buffer (it currently writes placeholder bytes). So we just
        compute the number of bytes produced and return that count.
        """
        if self._stream is None:
            return IoResult(-1, "not-open-input")

        # Each int16 sample is 2 bytes per channel.
        bytes_per_frame = 2 * self.channels
        frames = max(1, n // bytes_per_frame)

        try:
            data, overflowed = self._stream.read(frames)
            # data is a NumPy array; convert to bytes to know the length
            buf = data.tobytes()
            # Trim or pad to approximate n if desired; here we just report len(buf).
            return IoResult(len(buf), "")
        except Exception as e:
            return IoResult(0, f"read-error:{e}")

    def write(self, data: bytes) -> IoResult:
        """
        MicrophoneDevice is input-only; writing is not supported.
        Writer() should never use this device.
        """
        return IoResult(-1, "write-not-supported")

    def is_connected(self) -> bool:
        return self._stream is not None

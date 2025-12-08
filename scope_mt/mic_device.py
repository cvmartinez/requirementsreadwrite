# scope_mt/mic_device.py
import sounddevice as sd


class MicrophoneDevice:
    """
    Simple microphone-backed device that mimics the MockFtdiDevice interface:

      - open()
      - read_chunk(nbytes=16) -> bytes
      - close()

    It uses the default system input device (your default microphone).
    """

    def __init__(self, samplerate=44100, channels=1):
        self.samplerate = samplerate
        self.channels = channels
        self.stream = None
        self._open = False

    def open(self):
        if self._open:
            return

        # Blocking input stream, 16-bit mono
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype="int16",
        )
        self.stream.start()
        self._open = True

    def read_chunk(self, nbytes=16):
        """
        Read roughly nbytes of audio from the microphone and return as bytes.
        Each sample is int16 (2 bytes). For mono, bytes_per_frame = 2.
        """
        if not self._open:
            raise RuntimeError("MicrophoneDevice not open")

        bytes_per_frame = 2 * self.channels  # int16 per channel
        frames = max(1, nbytes // bytes_per_frame)

        data, overflowed = self.stream.read(frames)
        # data.shape == (frames, channels), dtype=int16
        # Down-mix to mono if needed and return raw bytes
        mono = data[:, 0]
        return mono.tobytes()

    def close(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self._open = False

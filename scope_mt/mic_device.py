import sounddevice as sd


class scpMicrophoneDevice:
    """
    Simple microphone-backed device that mimics an FTDI-like read_chunk API.
    """

    def __init__(self, samplerate=44100, channels=1):
        self.samplerate = samplerate
        self.channels = channels
        self.stream = None
        self._open = False

    def open(self):
        if self._open:
            return
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype="int16",
        )
        self.stream.start()
        self._open = True

    def read_chunk(self, nbytes=256):
        if not self._open:
            raise RuntimeError("scpMicrophoneDevice not open")

        bytes_per_frame = 2 * self.channels
        frames = max(1, nbytes // bytes_per_frame)
        data, _ = self.stream.read(frames)
        mono = data[:, 0]
        return mono.tobytes()

    def close(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self._open = False

import threading


class scpStopToken:
    """Thread-safe stop flag shared between threads."""

    def __init__(self) -> None:
        self._event = threading.Event()

    def stop(self) -> None:
        self._event.set()

    def is_stopped(self) -> bool:
        return self._event.is_set()

import time


class scpLogger:
    """
    Tiny logger wrapper to keep logging concerns separate.
    """

    def log(self, message: str) -> None:
        ts = time.strftime("%H:%M:%S", time.localtime())
        print(f"[scpLogger {ts}] {message}")

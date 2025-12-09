import threading
import time


class scpTimerThread(threading.Thread):
    """
    Simple timer thread that sleeps for a duration then calls a callback.
    """

    def __init__(self, duration_s: float, callback):
        super().__init__(daemon=True)
        self.duration_s = duration_s
        self.callback = callback

    def run(self):
        time.sleep(self.duration_s)
        self.callback()

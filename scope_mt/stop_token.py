import threading


class StopToken:
    def __init__(self):
        self._ev = threading.Event()

    def stop(self):
        self._ev.set()

    def stopped(self):
        return self._ev.is_set()

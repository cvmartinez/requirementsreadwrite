class scpStopToken:
    """
    Cooperative stop flag for threads/loops.
    """

    def __init__(self) -> None:
        self._stopped = False

    def stop(self) -> None:
        self._stopped = True

    def stopped(self) -> bool:
        return self._stopped

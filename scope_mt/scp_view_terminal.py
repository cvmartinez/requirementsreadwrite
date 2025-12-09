from .scp_logger import scpLogger


class scpTerminalView:
    """
    Terminal-based View for the oscilloscope.
    """

    def __init__(self, logger: scpLogger | None = None) -> None:
        self._logger = logger or scpLogger()

    def show_sample(self, t: float, value: float) -> None:
        """
        Display a single processed sample at time t (seconds).
        """
        self._logger.log(f"t={t:8.3f}s  value={value: .5f}")

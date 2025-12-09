import time

from .scp_config import scpConfig
from .scp_signal_source import scpSignalSource
from .scp_pipeline import scpPipelineProcessor
from .scp_loop_controller import scpLoopController
from .scp_stop_token import scpStopToken
from .scp_view_terminal import scpTerminalView
from .scp_logger import scpLogger


class scpReader:
    """
    Reads samples from the SignalSource, passes them through the pipeline,
    stores them in a buffer, and forwards them to the View.
    """

    def __init__(
        self,
        config: scpConfig,
        source: scpSignalSource,
        pipeline: scpPipelineProcessor,
        loop: scpLoopController,
        stop_token: scpStopToken,
        view: scpTerminalView,
        logger: scpLogger,
    ) -> None:
        self._config = config
        self._source = source
        self._pipeline = pipeline
        self._loop = loop
        self._stop_token = stop_token
        self._view = view
        self._logger = logger

        self.buffer: list[float] = []

    def run(self) -> None:
        """
        Main acquisition loop; designed to be run in a background thread.
        """

        self._logger.log("scpReader started")
        start_time = time.time()

        while not self._stop_token.stopped():
            raw = self._source.next_sample()
            processed = self._pipeline.process(raw)
            self.buffer.append(processed)

            t = time.time() - start_time
            self._view.show_sample(t, processed)

            time.sleep(self._loop.get_sleep_interval())

        self._logger.log("scpReader stopped")

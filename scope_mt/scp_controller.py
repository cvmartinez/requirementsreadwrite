import threading
import time

from .scp_config import scpConfig
from .scp_signal_source import scpSignalSource
from .scp_pipeline import scpPipelineProcessor
from .scp_stop_token import scpStopToken
from .scp_loop_controller import scpLoopController
from .scp_logger import scpLogger
from .scp_reader import scpReader
from .scp_view_terminal import scpTerminalView


class scpController:
    """
    Controller that wires together:
      - Config (scpConfig)
      - Model: scpSignalSource, scpPipelineProcessor, scpReader
      - View: scpTerminalView
    And manages the lifetime of the acquisition threads.
    """

    def __init__(self, logger: scpLogger | None = None) -> None:
        self._logger = logger or scpLogger()

    def run_scope(self, config: scpConfig) -> list[float]:
        """
        Run one acquisition based on the configuration.
        Spawns:
          - Reader thread (I/O + processing)
          - Timer thread (stops after config.duration)
        """

        stop_token = scpStopToken()
        loop = scpLoopController(config.sample_time)
        view = scpTerminalView(self._logger)

        source = scpSignalSource(
            freq_hz=config.freq_hz,
            amplitude=config.amplitude,
            sample_time=config.sample_time,
        )
        pipeline = scpPipelineProcessor(
            scale=config.scale,
            offset=config.offset,
        )

        reader = scpReader(
            config=config,
            source=source,
            pipeline=pipeline,
            loop=loop,
            stop_token=stop_token,
            view=view,
            logger=self._logger,
        )

        def _timer_thread() -> None:
            self._logger.log(f"Timer started for {config.duration:.3f} s")
            time.sleep(config.duration)
            self._logger.log("Timer expired; stopping acquisition.")
            stop_token.stop()

        t_reader = threading.Thread(target=reader.run, name="scpReaderThread", daemon=True)
        t_timer = threading.Thread(target=_timer_thread, name="scpTimerThread", daemon=True)

        t_reader.start()
        t_timer.start()

        # Wait for reader to finish, then ensure stop flag
        t_reader.join()
        stop_token.stop()
        t_timer.join()

        return reader.buffer

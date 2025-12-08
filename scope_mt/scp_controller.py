import threading
from scp_config import scpConfig
from scp_signal_source import scpSignalSource
from scp_pipeline import scpPipelineProcessor
from scp_stop_token import scpStopToken
from scp_loop_controller import scpLoopController
from scp_logger import scpLogger
from scp_reader import scpReader
from scp_view_terminal import scpTerminalView



class scpController:
    """
    Controller that wires together Config, Model (Reader + Source + Pipeline),
    and View, and manages the timer thread.
    """

    def __init__(self, logger: scpLogger | None = None) -> None:
        self._logger = logger or scpLogger()

    def run_scope(self, config: scpConfig):
        stop_token = scpStopToken()
        loop = scpLoopController(config.sample_time)
        view = scpTerminalView()

        source = scpSignalSource(
            freq_hz=config.freq_hz,
            amplitude=config.amplitude,
            sample_time=config.sample_time,
        )
        processor = scpPipelineProcessor(scale=config.scale, offset=config.offset)
        reader = scpReader(config, source, processor, loop, stop_token, view, self._logger)

        # Timer thread: stops acquisition after `duration` seconds.
        def _timer():
            self._logger.log(f"Timer started for {config.duration:.3f} s")
            import time as _time

            _time.sleep(config.duration)
            self._logger.log("Timer expired; stopping acquisition.")
            stop_token.stop()

        t_io = threading.Thread(target=reader.run, name="IoThread")
        t_timer = threading.Thread(target=_timer, name="TimerThread")

        t_io.start()
        t_timer.start()

        t_io.join()
        stop_token.stop()
        t_timer.join()

        return reader.buffer

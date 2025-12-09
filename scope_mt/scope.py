"""
scope.py
Entry point for the oscilloscope application.
Supports both CLI and GUI modes using the same controller and model.
"""

import sys

try:
    # Package-style imports: python -m scope_mt.scope --cli/--ui
    from .scp_config import scpConfig
    from .scp_controller import scpController
except ImportError:
    # Script-style imports: python scope.py --cli/--ui (from inside scope_mt)
    from scp_config import scpConfig
    from scp_controller import scpController


def parse_args(argv):
    """
    Supported CLI tokens:
      sampleTime=1ms or sampleTime=0.001s
      sampleFor=5s   or wait=5s
      scale=1.0
      offset=0.0
    """

    sample_time_ms = 1.0
    duration_s = 5.0
    scale = 1.0
    offset = 0.0
    freq_hz = 2.0
    amplitude = 1.0

    for token in argv:
        if token.startswith("sampleTime="):
            value = token.split("=", 1)[1].strip()
            if value.endswith("ms"):
                sample_time_ms = float(value[:-2])
            elif value.endswith("s"):
                sample_time_ms = float(value[:-1]) * 1000.0
        elif token.startswith("wait=") or token.startswith("sampleFor="):
            value = token.split("=", 1)[1].strip()
            if value.endswith("s"):
                duration_s = float(value[:-1])
        elif token.startswith("scale="):
            scale = float(token.split("=", 1)[1])
        elif token.startswith("offset="):
            offset = float(token.split("=", 1)[1])

    sample_time_s = sample_time_ms / 1000.0

    return scpConfig(
        sample_time=sample_time_s,
        duration=duration_s,
        scale=scale,
        offset=offset,
        freq_hz=freq_hz,
        amplitude=amplitude,
    )


def main():
    argv = sys.argv[1:]

    mode = "cli"
    if "--ui" in argv:
        mode = "ui"
        argv = [a for a in argv if a != "--ui"]
    if "--cli" in argv:
        mode = "cli"
        argv = [a for a in argv if a != "--cli"]

    if mode == "ui":
        try:
            from .scp_gui import main as gui_main
        except ImportError:
            from scp_gui import main as gui_main
        gui_main()
        return

    # CLI mode
    config = parse_args(argv)
    controller = scpController()
    controller.run_scope(config)


if __name__ == "__main__":
    main()

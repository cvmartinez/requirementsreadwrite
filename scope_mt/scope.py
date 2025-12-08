import sys
from scp_config import scpConfig
from scp_controller import scpController


def parse_args(argv):
    """
    For: python scope.py start sampleTime=1ms wait=5s stop
    We just care about sampleTime and wait/sampleFor.
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
    args = sys.argv[1:]  # e.g. ['start', 'sampleTime=1ms', 'wait=5s', 'stop']
    config = parse_args(args)
    controller = scpController()
    controller.run_scope(config)


if __name__ == "__main__":
    main()


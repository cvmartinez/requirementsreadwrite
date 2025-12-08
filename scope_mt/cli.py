import argparse
import re
from scp_config import scpConfig
from scp_controller import scpController

from .scp_config import scpConfig
from .scp_controller import scpController


def _parse_time_token(value: str) -> float:
    """
    Parse '10s' or '1ms' into seconds.
    """
    value = value.strip()
    m = re.match(r"^([0-9]*\.?[0-9]+)\s*(ms|s)$", value)
    if not m:
        raise ValueError(f"Invalid time spec: {value!r}")
    num = float(m.group(1))
    unit = m.group(2)
    if unit == "ms":
        return num / 1000.0
    return num


def parse_script(script: str) -> scpConfig:
    """
    Parse a script like:
      "scope start, sampleTime=1ms, sampleFor=10s, scale=2.0, offset=-0.2, freq=5, amp=1.5, stop"
    into an scpConfig.
    """
    parts = [p.strip() for p in script.split(",") if p.strip()]
    if not parts or not parts[0].lower().startswith("scope"):
        raise ValueError("Script must start with 'scope'.")

    # Ignore 'scope start' ... 'stop'
    key_tokens = parts[1:-1]

    kwargs: dict[str, float] = {
        "sample_time": 0.001,
        "duration": 5.0,
        "scale": 1.0,
        "offset": 0.0,
        "freq_hz": 2.0,
        "amplitude": 1.0,
    }

    for tok in key_tokens:
        if "=" not in tok:
            continue
        key, val = [x.strip() for x in tok.split("=", 1)]
        key_lower = key.lower()

        if key_lower == "sampletime":
            kwargs["sample_time"] = _parse_time_token(val)
        elif key_lower in ("samplefor", "duration"):
            kwargs["duration"] = _parse_time_token(val)
        elif key_lower == "scale":
            kwargs["scale"] = float(val)
        elif key_lower == "offset":
            kwargs["offset"] = float(val)
        elif key_lower in ("freq", "frequency"):
            kwargs["freq_hz"] = float(val)
        elif key_lower in ("amp", "amplitude"):
            kwargs["amplitude"] = float(val)

    return scpConfig(**kwargs)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Oscilloscope demo using internal sine generator (terminal view)."
    )
    parser.add_argument(
        "script",
        help=(
            "Command script, e.g.: "
            '"scope start, sampleTime=1ms, sampleFor=10s, scale=2.0, offset=-0.1, stop"'
        ),
    )
    args = parser.parse_args()

    config = parse_script(args.script)
    controller = scpController()
    controller.run_scope(config)


if __name__ == "__main__":
    main()

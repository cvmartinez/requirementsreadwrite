# scp_cli_view.py
"""
Terminal (CLI) View for the Oscilloscope.

This file implements ONLY presentation + input parsing.
All business logic is delegated to the Controller.
"""

from typing import List
from scp_view_terminal import scpTerminalView


def run_cli(controller, model, argv: List[str]) -> None:
    """
    Run the interactive CLI oscilloscope.

    Args:
        controller: shared scpController instance
        model: shared scpSignalModel instance
        argv: remaining command-line arguments (unused for now)
    """

    print("\nscope --cli")
    print("Commands:")
    print("  scope start")
    print("  scope sampleTime=1ms")
    print("  scope sampleFor=10s")
    print("  scope scale=2.0")
    print("  scope offset=0.5")
    print("  scope stop")
    print("  exit\n")

    # Terminal View instance
    view = scpTerminalView()

    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nexit")
            break

        if not line:
            continue

        if line.lower() == "exit":
            break

        # Allow "scope X" or just "X"
        if line.lower().startswith("scope "):
            cmd = line[6:].strip()
        else:
            cmd = line

        try:
            _dispatch_command(cmd, controller, view)
        except Exception as e:
            print(f"Error: {e}")


# ----------------------------------------------------------------------
# Command dispatch (CLI -> Controller)
# ----------------------------------------------------------------------

def _dispatch_command(cmd: str, controller, view) -> None:
    """
    Map CLI commands to controller calls.
    """

    if cmd == "start":
        controller.start_acquisition(view=view)

    elif cmd == "stop":
        controller.stop_acquisition()

    elif cmd.startswith("sampleTime="):
        value = _parse_time(cmd.split("=", 1)[1])
        controller.set_sample_time(value)

    elif cmd.startswith("sampleFor="):
        value = _parse_time(cmd.split("=", 1)[1])
        controller.set_sample_for(value)

    elif cmd.startswith("scale="):
        controller.set_scale(float(cmd.split("=", 1)[1]))

    elif cmd.startswith("offset="):
        controller.set_offset(float(cmd.split("=", 1)[1]))

    else:
        print(
            "Unknown command.\n"
            "Valid commands:\n"
            "  scope start\n"
            "  scope sampleTime=1ms\n"
            "  scope sampleFor=10s\n"
            "  scope scale=2.0\n"
            "  scope offset=0.5\n"
            "  scope stop\n"
            "  exit"
        )


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _parse_time(token: str) -> float:
    """
    Parse time values like '1ms' or '10s' into seconds.
    """
    token = token.strip().lower()

    if token.endswith("ms"):
        return float(token[:-2]) / 1000.0

    if token.endswith("s"):
        return float(token[:-1])

    # Default: assume seconds
    return float(token)

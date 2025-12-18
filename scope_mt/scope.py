# scope.py
import sys

from scp_signal_model import scpSignalModel
from scp_controller import scpController
from scp_cli_view import run_cli
from scp_gui import run_gui


def main() -> None:
    argv = sys.argv[1:]

    mode = "cli"
    if "--ui" in argv:
        mode = "ui"
        argv = [a for a in argv if a != "--ui"]
    if "--cli" in argv:
        mode = "cli"
        argv = [a for a in argv if a != "--cli"]

    model = scpSignalModel(max_points=2000)
    controller = scpController(model)

    if mode == "ui":
        run_gui(controller, model)
    else:
        run_cli(controller, model, argv)


if __name__ == "__main__":
    main()

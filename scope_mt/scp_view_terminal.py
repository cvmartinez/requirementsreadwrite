# scp_terminal_view.py
class scpTerminalView:
    """
    Terminal-based View: prints samples.
    """

    def show_sample(self, t: float, value: float) -> None:
        print(f"t={t:8.3f}s  value={value: .5f}")

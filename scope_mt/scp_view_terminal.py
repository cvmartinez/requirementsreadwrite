class scpTerminalView:
    """
    Text-based oscilloscope view.
    Prints samples so they scroll down the terminal.
    """

    def render_sample(self, index: int, value: float) -> None:
        print(f"{index:06d}: {value: .4f}")

    def render_summary(self, total_samples: int, duration: float, eff_rate: float) -> None:
        print("\n--- Acquisition Summary ---")
        print(f"Samples:   {total_samples}")
        print(f"Duration:  {duration:.3f} s")
        print(f"Eff. rate: {eff_rate:.1f} samples/s")

class scpLoopController:
    """
    Very simple loop controller that owns the sampling interval.
    """

    def __init__(self, sample_time: float) -> None:
        self.sample_time = sample_time

    def get_sleep_interval(self) -> float:
        return self.sample_time

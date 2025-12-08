class scpPipelineProcessor:
    """
    Simple pipe-and-filter style processor that applies scaling and offset.
    """

    def __init__(self, scale: float = 1.0, offset: float = 0.0) -> None:
        self.scale = scale
        self.offset = offset

    def process(self, sample: float) -> float:
        return sample * self.scale + self.offset

class scpPipelineProcessor:
    """
    Simple processing pipeline that applies scale and offset to a raw sample.
    """

    def __init__(self, scale: float = 1.0, offset: float = 0.0) -> None:
        self.scale = scale
        self.offset = offset

    def process(self, value: float) -> float:
        """Apply scale and offset and return the processed value."""
        return self.scale * value + self.offset

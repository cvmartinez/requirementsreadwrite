# oscifgen/__init__.py
from .reader import Reader
from .writer import Writer
from .wavegen import Wave, make_wave

__all__ = ["Reader", "Writer", "Wave", "make_wave"]
__version__ = "0.1.0"

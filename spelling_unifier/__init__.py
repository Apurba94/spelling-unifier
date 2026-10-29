"""Find and unify mixed US/UK spelling in manuscripts."""
from .core import VARIANTS, find_variants, dominant_style, unify

__version__ = "0.1.0"
__all__ = ["VARIANTS", "find_variants", "dominant_style", "unify"]

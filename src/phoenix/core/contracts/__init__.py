"""
Core contracts.

These types form the common language used throughout the Phoenix Platform.
"""

from __future__ import annotations

from .error import ErrorCode, ErrorSeverity, PhoenixError
from .outcome import Outcome
from .result import Result

__all__ = [
    "Result",
    "PhoenixError",
    "ErrorCode",
    "ErrorSeverity",
    "Outcome",
]

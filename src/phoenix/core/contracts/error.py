"""
Structured error contracts.

Expected failures in Phoenix are represented using PhoenixError rather
than arbitrary exceptions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class ErrorSeverity(str, Enum):
    """
    Severity of an error.
    """

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class ErrorCode:
    """
    Stable error identifier.

    Example:

        CORE001
        CFG104
        WF208
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Error code cannot be empty.")


@dataclass(frozen=True, slots=True)
class PhoenixError:
    """
    Structured platform error.
    """

    code: ErrorCode

    message: str

    severity: ErrorSeverity = ErrorSeverity.ERROR

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    cause: Exception | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

        if not self.message:
            raise ValueError("Error message cannot be empty.")

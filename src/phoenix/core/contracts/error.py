"""
Structured error model used throughout the Phoenix Platform.

Expected failures are represented by PhoenixError and propagated through
Result.failure(...).

PhoenixError is immutable, serializable, and carries stable error codes
that allow tracing and analytics across the platform.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


Metadata = Mapping[str, Any]


class ErrorSeverity(str, Enum):
    """
    Severity level of an error.
    """

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class ErrorCode:
    """
    Stable identifier for an error.

    Examples:
        CORE001
        CFG102
        WF301
    """

    value: str

    def __post_init__(self) -> None:
        value = self.value.strip()

        if not value:
            raise ValueError("ErrorCode cannot be empty.")

        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class PhoenixError:
    """
    Represents an expected failure within the Phoenix Platform.

    Unlike Python exceptions, PhoenixError is intended to be returned
    through Result.failure() so that workflows remain composable.
    """

    code: ErrorCode

    message: str

    severity: ErrorSeverity = ErrorSeverity.ERROR

    metadata: Metadata = field(default_factory=dict)

    cause: Exception | None = None

    def __post_init__(self) -> None:
        if not self.message.strip():
            raise ValueError("Error message cannot be empty.")

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the error into a JSON-compatible dictionary.
        """

        return {
            "code": str(self.code),
            "message": self.message,
            "severity": self.severity.value,
            "metadata": dict(self.metadata),
            "cause": repr(self.cause) if self.cause else None,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PhoenixError":
        """
        Deserialize a PhoenixError from a dictionary.
        """

        return cls(
            code=ErrorCode(str(data["code"])),
            message=str(data["message"]),
            severity=ErrorSeverity(str(data["severity"])),
            metadata=dict(data.get("metadata", {})),
        )

    def with_metadata(self, **metadata: Any) -> "PhoenixError":
        """
        Return a new PhoenixError with merged metadata.
        """

        merged = dict(self.metadata)
        merged.update(metadata)

        return PhoenixError(
            code=self.code,
            message=self.message,
            severity=self.severity,
            metadata=merged,
            cause=self.cause,
        )

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

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
from typing import Any

class ErrorSeverity(str, Enum):
    INFO="info"
    WARNING="warning"
    ERROR="error"
    CRITICAL="critical"

@dataclass(frozen=True, slots=True)
class ErrorCode:
    value:str
    def __post_init__(self):
        if not self.value.strip():
            raise ValueError("ErrorCode cannot be empty.")

@dataclass(frozen=True, slots=True)
class PhoenixError:
    code: ErrorCode
    message:str
    severity:ErrorSeverity=ErrorSeverity.ERROR
    metadata:dict[str,Any]=field(default_factory=dict)
    cause:str|None=None

    def to_dict(self)->dict[str,Any]:
        return {
            "code": self.code.value,
            "message": self.message,
            "severity": self.severity.value,
            "metadata": self.metadata,
            "cause": self.cause,
        }

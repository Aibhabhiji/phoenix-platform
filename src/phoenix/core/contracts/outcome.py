"""
Operation outcome.

Outcome is a lightweight semantic wrapper around Result that can evolve
with workflow execution metadata in future releases.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from .result import Result

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Outcome(Generic[T]):
    """
    Represents the outcome of a Phoenix operation.
    """

    result: Result[T]

    @property
    def succeeded(self) -> bool:
        return self.result.is_success

    @property
    def failed(self) -> bool:
        return self.result.is_failure

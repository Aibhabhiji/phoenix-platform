"""
Result contract.

Represents either a successful value or a structured PhoenixError.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

from .error import PhoenixError

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class Result(Generic[T]):
    """
    Represents the outcome of an operation.

    Exactly one of value or error exists.
    """

    _value: T | None = None
    _error: PhoenixError | None = None

    def __post_init__(self) -> None:
        has_value = self._value is not None
        has_error = self._error is not None

        if has_value == has_error:
            raise ValueError(
                "A Result must contain exactly one of value or error."
            )

    @classmethod
    def success(cls, value: T) -> "Result[T]":
        return cls(_value=value)

    @classmethod
    def failure(cls, error: PhoenixError) -> "Result[T]":
        return cls(_error=error)

    @property
    def is_success(self) -> bool:
        return self._error is None

    @property
    def is_failure(self) -> bool:
        return self._error is not None

    @property
    def value(self) -> T:
        if self._value is None:
            raise ResultAccessError("Cannot access value of a failed Result.")

        return self._value

    @property
    def error(self) -> PhoenixError:
        if self._error is None:
            raise ResultAccessError("Cannot access error of a successful Result.")

        return self._error

    def map(self, mapper: Callable[[T], U]) -> "Result[U]":
        """
        Maps the success value.
        """
        if self.is_failure:
            return Result.failure(self.error)

        return Result.success(mapper(self.value))

    def bind(
        self,
        mapper: Callable[[T], "Result[U]"],
    ) -> "Result[U]":
        """
        Monadic bind.
        """
        if self.is_failure:
            return Result.failure(self.error)

        return mapper(self.value)

    def unwrap(self) -> T:
        """
        Returns the success value or raises RuntimeError.
        """
        return self.value

    def unwrap_or(self, default: T) -> T:
        """
        Returns the value or a default.
        """
        if self.is_success:
            return self.value

        return default

"""
Phoenix Result Contract.

The Result type represents the outcome of an operation that can either
succeed with a value or fail with a PhoenixError.

Expected failures should be represented as Result.failure(...) instead of
raising exceptions. Unexpected programming errors should still raise Python
exceptions.

This design is inspired by Rust's Result<T, E>, railway-oriented
programming, and modern functional error handling patterns.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Final, Generic, TypeVar, cast

from .error import PhoenixError
from .exceptions import InvalidResultError, ResultAccessError

T = TypeVar("T")
U = TypeVar("U")

# Sentinel object allowing Result.success(None)
_MISSING: Final = object()


@dataclass(frozen=True, slots=True)
class Result(Generic[T]):
    """
    Represents either a successful value or a PhoenixError.

    Exactly one of:

        value
        error

    exists.

    Examples
    --------

    >>> Result.success(42)

    >>> Result.failure(error)

    >>> Result.success(None)
    """

    _value: object = _MISSING
    _error: PhoenixError | None = None

    def __post_init__(self) -> None:
        has_value = self._value is not _MISSING
        has_error = self._error is not None

        if has_value == has_error:
            raise InvalidResultError(
                "A Result must contain either a value or an error."
            )

    # ------------------------------------------------------------------
    # Factory methods
    # ------------------------------------------------------------------

    @classmethod
    def success(cls, value: T) -> Result[T]:
        """
        Create a successful Result.
        """
        return cls(_value=value)

    @classmethod
    def failure(cls, error: PhoenixError) -> Result[T]:
        """
        Create a failed Result.
        """
        return cls(_error=error)

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    @property
    def is_success(self) -> bool:
        """
        True if the Result contains a value.
        """
        return self._error is None

    @property
    def is_failure(self) -> bool:
        """
        True if the Result contains an error.
        """
        return self._error is not None

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def value(self) -> T:
        """
        Return the success value.

        Raises
        ------
        ResultAccessError
            If this Result represents a failure.
        """
        if self.is_failure:
            raise ResultAccessError(
                "Cannot access value from a failed Result."
            )

        return cast(T, self._value)

    @property
    def error(self) -> PhoenixError:
        """
        Return the contained PhoenixError.

        Raises
        ------
        ResultAccessError
            If this Result represents success.
        """
        if self._error is None:
            raise ResultAccessError(
                "Cannot access error from a successful Result."
            )

        return self._error

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------

    def unwrap(self) -> T:
        """
        Return the contained value.

        Equivalent to accessing .value.
        """
        return self.value

    def unwrap_or(self, default: T) -> T:
        """
        Return the contained value or a default.
        """
        return self.value if self.is_success else default

    def unwrap_or_else(self, factory: Callable[[PhoenixError], T]) -> T:
        """
        Lazily compute a fallback value.
        """
        if self.is_success:
            return self.value

        return factory(self.error)

    # ------------------------------------------------------------------
    # Functional operators
    # ------------------------------------------------------------------

    def map(self, mapper: Callable[[T], U]) -> Result[U]:
        """
        Transform the success value.

        Errors propagate unchanged.
        """
        if self.is_failure:
            return Result.failure(self.error)

        return Result.success(mapper(self.value))

    def bind(self, mapper: Callable[[T], Result[U]]) -> Result[U]:
        """
        Flat-map operation.
        """
        if self.is_failure:
            return Result.failure(self.error)

        return mapper(self.value)

    def map_error(
        self,
        mapper: Callable[[PhoenixError], PhoenixError],
    ) -> Result[T]:
        """
        Transform only the error.
        """
        if self.is_success:
            return self

        return Result.failure(mapper(self.error))

    def inspect(self, callback: Callable[[T], Any]) -> Result[T]:
        """
        Execute a side-effect for successful values.

        Useful for logging and debugging.
        """
        if self.is_success:
            callback(self.value)

        return self

    def inspect_error(
        self,
        callback: Callable[[PhoenixError], Any],
    ) -> Result[T]:
        """
        Execute a side-effect for failures.
        """
        if self.is_failure:
            callback(self.error)

        return self

    def match(
        self,
        *,
        success: Callable[[T], U],
        failure: Callable[[PhoenixError], U],
    ) -> U:
        """
        Pattern-match the Result.
        """
        if self.is_success:
            return success(self.value)

        return failure(self.error)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize into a JSON-compatible dictionary.
        """
        if self.is_success:
            return {
                "success": True,
                "value": self.value,
            }

        return {
            "success": False,
            "error": self.error.to_dict(),
        }

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __bool__(self) -> bool:
        """
        Allows:

            if result:
                ...
        """
        return self.is_success

    def __repr__(self) -> str:
        if self.is_success:
            return f"Result.success({self.value!r})"

        return f"Result.failure({self.error!r})"

"""
Unit tests for the Phoenix Result contract.
"""

from __future__ import annotations

import pytest

from phoenix.core.contracts.error import (
    ErrorCode,
    ErrorSeverity,
    PhoenixError,
)
from phoenix.core.contracts.exceptions import (
    InvalidResultError,
    ResultAccessError,
)
from phoenix.core.contracts.result import Result


def create_error() -> PhoenixError:
    return PhoenixError(
        code=ErrorCode("CORE001"),
        message="Something went wrong.",
        severity=ErrorSeverity.ERROR,
    )


# ----------------------------------------------------------------------
# Construction
# ----------------------------------------------------------------------


def test_success_result():
    result = Result.success(42)

    assert result.is_success
    assert not result.is_failure
    assert result.value == 42


def test_failure_result():
    error = create_error()

    result = Result.failure(error)

    assert result.is_failure
    assert not result.is_success
    assert result.error == error


def test_success_none():
    result = Result.success(None)

    assert result.is_success
    assert result.value is None


def test_invalid_result_both_value_and_error():
    with pytest.raises(InvalidResultError):
        Result(
            _value=1,
            _error=create_error(),
        )


def test_invalid_result_empty():
    with pytest.raises(InvalidResultError):
        Result()


# ----------------------------------------------------------------------
# Value Access
# ----------------------------------------------------------------------


def test_value_from_failure():
    result = Result.failure(create_error())

    with pytest.raises(ResultAccessError):
        _ = result.value


def test_error_from_success():
    result = Result.success(100)

    with pytest.raises(ResultAccessError):
        _ = result.error


def test_unwrap_success():
    result = Result.success("phoenix")

    assert result.unwrap() == "phoenix"


def test_unwrap_or():
    success = Result.success(5)
    failure = Result.failure(create_error())

    assert success.unwrap_or(10) == 5
    assert failure.unwrap_or(10) == 10


def test_unwrap_or_else():
    result = Result.failure(create_error())

    value = result.unwrap_or_else(lambda _: 99)

    assert value == 99


# ----------------------------------------------------------------------
# Functional Operators
# ----------------------------------------------------------------------


def test_map_success():
    result = Result.success(5)

    mapped = result.map(lambda x: x * 2)

    assert mapped.value == 10


def test_map_failure():
    error = create_error()

    result = Result.failure(error)

    mapped = result.map(lambda x: x)

    assert mapped.error == error


def test_bind_success():
    result = Result.success(10)

    bound = result.bind(
        lambda value: Result.success(value + 5)
    )

    assert bound.value == 15


def test_bind_failure():
    error = create_error()

    result = Result.failure(error)

    bound = result.bind(
        lambda value: Result.success(value)
    )

    assert bound.error == error


def test_map_error():
    result = Result.failure(create_error())

    mapped = result.map_error(
        lambda e: PhoenixError(
            code=e.code,
            message="Updated",
            severity=e.severity,
        )
    )

    assert mapped.error.message == "Updated"


def test_match_success():
    result = Result.success(3)

    value = result.match(
        success=lambda x: x * 10,
        failure=lambda _: 0,
    )

    assert value == 30


def test_match_failure():
    result = Result.failure(create_error())

    value = result.match(
        success=lambda _: 1,
        failure=lambda _: -1,
    )

    assert value == -1


# ----------------------------------------------------------------------
# Inspection
# ----------------------------------------------------------------------


def test_inspect():
    captured = []

    result = Result.success(7)

    returned = result.inspect(
        lambda value: captured.append(value)
    )

    assert captured == [7]
    assert returned is result


def test_inspect_error():
    captured = []

    error = create_error()

    result = Result.failure(error)

    returned = result.inspect_error(
        lambda e: captured.append(e.message)
    )

    assert captured == ["Something went wrong."]
    assert returned is result


# ----------------------------------------------------------------------
# Serialization
# ----------------------------------------------------------------------


def test_success_serialization():
    result = Result.success(123)

    data = result.to_dict()

    assert data["success"] is True
    assert data["value"] == 123


def test_failure_serialization():
    result = Result.failure(create_error())

    data = result.to_dict()

    assert data["success"] is False
    assert data["error"]["code"] == "CORE001"


# ----------------------------------------------------------------------
# Boolean
# ----------------------------------------------------------------------


def test_bool_success():
    assert bool(Result.success(1))


def test_bool_failure():
    assert not bool(Result.failure(create_error()))


# ----------------------------------------------------------------------
# Equality
# ----------------------------------------------------------------------


def test_success_equality():
    assert Result.success(1) == Result.success(1)


def test_failure_equality():
    error = create_error()

    assert Result.failure(error) == Result.failure(error)


# ----------------------------------------------------------------------
# Hashing
# ----------------------------------------------------------------------


def test_hash_success():
    result = Result.success(1)

    assert hash(result)


def test_hash_failure():
    result = Result.failure(create_error())

    assert hash(result)


# ----------------------------------------------------------------------
# Representation
# ----------------------------------------------------------------------


def test_repr_success():
    text = repr(Result.success(1))

    assert "Result" in text


def test_repr_failure():
    text = repr(Result.failure(create_error()))

    assert "Result" in text

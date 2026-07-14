
"""
Exceptions used by the Phoenix Core Contracts package.

These exceptions indicate incorrect usage of the Result contract itself.
Business failures should be represented by PhoenixError and returned inside
Result.failure(...), not raised.
"""

from __future__ import annotations


class PhoenixContractError(Exception):
    """
    Base exception for contract violations within Phoenix Core.
    """


class InvalidResultError(PhoenixContractError):
    """
    Raised when a Result is constructed with an invalid state.

    A Result must contain either a success value or a PhoenixError,
    but never both and never neither.
    """


class ResultAccessError(PhoenixContractError):
    """
    Raised when attempting to access the wrong side of a Result.

    Examples:
        * Accessing .value on a failed Result.
        * Accessing .error on a successful Result.
    """

"""
Phoenix Outcome Contract.

Outcome represents the execution of an operation.

Unlike Result, which models only success or failure, Outcome also
captures execution metadata that becomes important for tracing,
evaluation, governance and telemetry.

Every workflow step, agent invocation and provider execution in Phoenix
will eventually return an Outcome.

The design intentionally keeps the metadata optional so that the API is
stable while allowing future expansion.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any, Generic, Mapping, TypeVar
from uuid import UUID, uuid4

from .result import Result

T = TypeVar("T")


Metadata = Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class Outcome(Generic[T]):
    """
    Represents the execution outcome of an operation.

    Parameters
    ----------
    result
        Success or failure of the operation.

    correlation_id
        Unique identifier used for distributed tracing.

    started_at
        UTC timestamp indicating when execution started.

    completed_at
        UTC timestamp indicating when execution finished.

    metadata
        Immutable execution metadata.

    Notes
    -----
    Unlike Result, Outcome is expected to grow over time with additional
    execution information while preserving backwards compatibility.
    """

    result: Result[T]

    correlation_id: UUID = field(default_factory=uuid4)

    started_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    completed_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    metadata: Metadata = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

        if self.completed_at < self.started_at:
            raise ValueError(
                "completed_at cannot be earlier than started_at."
            )

    # ------------------------------------------------------------
    # Status
    # ------------------------------------------------------------

    @property
    def succeeded(self) -> bool:
        """
        Returns True when the operation completed successfully.
        """
        return self.result.is_success

    @property
    def failed(self) -> bool:
        """
        Returns True when the operation failed.
        """
        return self.result.is_failure

    # ------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------

    @property
    def duration(self):
        """
        Returns the execution duration.

        Returns
        -------
        timedelta
        """
        return self.completed_at - self.started_at

    # ------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------

    def with_metadata(self, **metadata: Any) -> "Outcome[T]":
        """
        Return a new Outcome with merged metadata.

        Outcome instances are immutable.
        """

        merged = dict(self.metadata)
        merged.update(metadata)

        return Outcome(
            result=self.result,
            correlation_id=self.correlation_id,
            started_at=self.started_at,
            completed_at=self.completed_at,
            metadata=merged,
        )

    # ------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the Outcome into a JSON-compatible dictionary.
        """

        return {
            "correlation_id": str(self.correlation_id),
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "duration_seconds": self.duration.total_seconds(),
            "result": self.result.to_dict(),
            "metadata": dict(self.metadata),
        }

    # ------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            "Outcome("
            f"success={self.succeeded}, "
            f"duration={self.duration}, "
            f"correlation_id={self.correlation_id}"
            ")"
        )

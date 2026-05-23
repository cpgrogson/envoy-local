"""Timeout policy configuration for Envoy routes."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TimeoutPolicy:
    """Defines per-route timeout settings."""
    route_timeout_seconds: float = 15.0
    idle_timeout_seconds: Optional[float] = None
    per_try_timeout_seconds: Optional[float] = None

    def validate(self) -> list:
        """Return a list of validation error strings, empty if valid."""
        errors = []
        if self.route_timeout_seconds < 0:
            errors.append("route_timeout_seconds must be non-negative")
        if self.idle_timeout_seconds is not None and self.idle_timeout_seconds <= 0:
            errors.append("idle_timeout_seconds must be positive")
        if self.per_try_timeout_seconds is not None and self.per_try_timeout_seconds <= 0:
            errors.append("per_try_timeout_seconds must be positive")
        if (
            self.per_try_timeout_seconds is not None
            and self.route_timeout_seconds > 0
            and self.per_try_timeout_seconds > self.route_timeout_seconds
        ):
            errors.append(
                "per_try_timeout_seconds must not exceed route_timeout_seconds"
            )
        return errors

    def to_envoy_dict(self) -> dict:
        """Serialize to Envoy route action timeout fields."""
        result: dict = {
            "timeout": f"{self.route_timeout_seconds}s",
        }
        if self.idle_timeout_seconds is not None:
            result["idle_timeout"] = f"{self.idle_timeout_seconds}s"
        if self.per_try_timeout_seconds is not None:
            result["per_try_timeout"] = f"{self.per_try_timeout_seconds}s"
        return result


def default_timeout_policy() -> TimeoutPolicy:
    """Return a sensible default timeout policy."""
    return TimeoutPolicy(
        route_timeout_seconds=15.0,
        idle_timeout_seconds=None,
        per_try_timeout_seconds=None,
    )

"""Circuit breaker policy configuration for Envoy clusters."""

from dataclasses import dataclass, field
from typing import Optional


class CircuitBreakerError(Exception):
    pass


@dataclass
class CircuitBreakerThresholds:
    max_connections: int = 1024
    max_pending_requests: int = 1024
    max_requests: int = 1024
    max_retries: int = 3
    priority: str = "DEFAULT"

    def validate(self) -> None:
        if self.max_connections <= 0:
            raise CircuitBreakerError("max_connections must be positive")
        if self.max_pending_requests <= 0:
            raise CircuitBreakerError("max_pending_requests must be positive")
        if self.max_requests <= 0:
            raise CircuitBreakerError("max_requests must be positive")
        if self.max_retries < 0:
            raise CircuitBreakerError("max_retries must be non-negative")
        if self.priority not in ("DEFAULT", "HIGH"):
            raise CircuitBreakerError("priority must be 'DEFAULT' or 'HIGH'")

    def to_envoy_dict(self) -> dict:
        self.validate()
        return {
            "priority": self.priority,
            "max_connections": self.max_connections,
            "max_pending_requests": self.max_pending_requests,
            "max_requests": self.max_requests,
            "max_retries": self.max_retries,
        }


@dataclass
class CircuitBreakerPolicy:
    thresholds: list = field(default_factory=lambda: [CircuitBreakerThresholds()])

    def validate(self) -> None:
        if not self.thresholds:
            raise CircuitBreakerError("at least one threshold is required")
        for t in self.thresholds:
            t.validate()

    def to_envoy_dict(self) -> dict:
        self.validate()
        return {
            "thresholds": [t.to_envoy_dict() for t in self.thresholds]
        }


def default_circuit_breaker() -> CircuitBreakerPolicy:
    """Return a sensible default circuit breaker policy."""
    return CircuitBreakerPolicy(
        thresholds=[
            CircuitBreakerThresholds(
                max_connections=1024,
                max_pending_requests=1024,
                max_requests=1024,
                max_retries=3,
                priority="DEFAULT",
            )
        ]
    )

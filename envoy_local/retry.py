"""Retry policy configuration for Envoy routes."""
from dataclasses import dataclass, field
from typing import List, Optional


RETRY_ON_OPTIONS = {
    "5xx",
    "gateway-error",
    "reset",
    "connect-failure",
    "retriable-4xx",
    "refused-stream",
    "retriable-status-codes",
}


@dataclass
class RetryPolicy:
    num_retries: int = 2
    retry_on: List[str] = field(default_factory=lambda: ["5xx", "gateway-error"])
    per_try_timeout_seconds: Optional[float] = None
    retry_host_predicate: Optional[str] = None

    def validate(self) -> List[str]:
        """Return a list of validation error strings, empty if valid."""
        errors: List[str] = []
        if self.num_retries < 0:
            errors.append(f"num_retries must be >= 0, got {self.num_retries}")
        unknown = set(self.retry_on) - RETRY_ON_OPTIONS
        if unknown:
            errors.append(f"Unknown retry_on values: {sorted(unknown)}")
        if not self.retry_on:
            errors.append("retry_on must contain at least one value")
        if self.per_try_timeout_seconds is not None and self.per_try_timeout_seconds <= 0:
            errors.append(
                f"per_try_timeout_seconds must be > 0, got {self.per_try_timeout_seconds}"
            )
        return errors

    def to_envoy_dict(self) -> dict:
        """Render this retry policy as an Envoy xDS-compatible dict."""
        d: dict = {
            "retry_on": ",".join(self.retry_on),
            "num_retries": self.num_retries,
        }
        if self.per_try_timeout_seconds is not None:
            d["per_try_timeout"] = f"{self.per_try_timeout_seconds}s"
        if self.retry_host_predicate:
            d["retry_host_predicate"] = [
                {"name": self.retry_host_predicate}
            ]
        return d


def default_retry_policy() -> RetryPolicy:
    """Return a sensible default retry policy."""
    return RetryPolicy(
        num_retries=2,
        retry_on=["5xx", "gateway-error", "connect-failure"],
        per_try_timeout_seconds=2.0,
    )

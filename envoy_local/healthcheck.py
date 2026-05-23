"""Health check configuration helpers for Envoy upstream clusters."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HealthCheckConfig:
    """Represents an active health check configuration for an upstream."""

    path: str = "/healthz"
    interval_seconds: int = 10
    timeout_seconds: int = 5
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    port: Optional[int] = None

    def validate(self) -> list:
        """Return a list of validation error strings, empty if valid."""
        errors = []
        if self.interval_seconds <= 0:
            errors.append("interval_seconds must be positive")
        if self.timeout_seconds <= 0:
            errors.append("timeout_seconds must be positive")
        if self.timeout_seconds >= self.interval_seconds:
            errors.append("timeout_seconds must be less than interval_seconds")
        if self.healthy_threshold < 1:
            errors.append("healthy_threshold must be at least 1")
        if self.unhealthy_threshold < 1:
            errors.append("unhealthy_threshold must be at least 1")
        if self.port is not None and not (1 <= self.port <= 65535):
            errors.append(f"port {self.port} is out of valid range 1-65535")
        if not self.path.startswith("/"):
            errors.append("path must start with '/'")
        return errors

    def to_envoy_dict(self) -> dict:
        """Render this config as an Envoy health_checks dict fragment."""
        hc: dict = {
            "timeout": f"{self.timeout_seconds}s",
            "interval": f"{self.interval_seconds}s",
            "healthy_threshold": self.healthy_threshold,
            "unhealthy_threshold": self.unhealthy_threshold,
            "http_health_check": {"path": self.path},
        }
        if self.port is not None:
            hc["http_health_check"]["host"] = ""
            hc["alt_port"] = self.port
        return hc


def default_health_check() -> HealthCheckConfig:
    """Return a sensible default health check configuration."""
    return HealthCheckConfig()

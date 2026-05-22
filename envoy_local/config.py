"""Core configuration models for Envoy proxy generation."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class UpstreamService:
    """Represents a single upstream service cluster."""
    name: str
    host: str
    port: int
    health_check_path: Optional[str] = "/healthz"

    def cluster_name(self) -> str:
        return self.name.replace("-", "_").lower()


@dataclass
class ListenerConfig:
    """Configuration for the Envoy listener (front proxy)."""
    address: str = "0.0.0.0"
    port: int = 10000


@dataclass
class EnvoyConfig:
    """Top-level configuration object for a local Envoy proxy setup."""
    listener: ListenerConfig = field(default_factory=ListenerConfig)
    upstreams: List[UpstreamService] = field(default_factory=list)
    admin_port: int = 9901
    log_level: str = "info"

    def add_upstream(self, name: str, host: str, port: int, health_check_path: Optional[str] = "/healthz") -> None:
        """Convenience method to register an upstream service."""
        self.upstreams.append(
            UpstreamService(
                name=name,
                host=host,
                port=port,
                health_check_path=health_check_path,
            )
        )

    def validate(self) -> None:
        """Raise ValueError if the configuration is invalid."""
        if not self.upstreams:
            raise ValueError("At least one upstream service must be defined.")
        names = [u.name for u in self.upstreams]
        if len(names) != len(set(names)):
            raise ValueError("Upstream service names must be unique.")
        if not (1 <= self.listener.port <= 65535):
            raise ValueError(f"Invalid listener port: {self.listener.port}")
        if not (1 <= self.admin_port <= 65535):
            raise ValueError(f"Invalid admin port: {self.admin_port}")

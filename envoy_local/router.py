"""Route configuration builder for Envoy virtual hosts."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RouteMatch:
    prefix: str = "/"
    headers: List[dict] = field(default_factory=list)

    def to_envoy_dict(self) -> dict:
        match: dict = {"prefix": self.prefix}
        if self.headers:
            match["headers"] = self.headers
        return match


@dataclass
class RouteAction:
    cluster: str
    timeout_seconds: int = 15
    retry_on: Optional[str] = None
    num_retries: int = 1

    def to_envoy_dict(self) -> dict:
        action: dict = {
            "cluster": self.cluster,
            "timeout": f"{self.timeout_seconds}s",
        }
        if self.retry_on:
            action["retry_policy"] = {
                "retry_on": self.retry_on,
                "num_retries": self.num_retries,
            }
        return action


@dataclass
class RouteEntry:
    match: RouteMatch
    action: RouteAction

    def to_envoy_dict(self) -> dict:
        return {
            "match": self.match.to_envoy_dict(),
            "route": self.action.to_envoy_dict(),
        }


class RouteError(Exception):
    pass


def build_routes(
    cluster: str,
    prefix: str = "/",
    timeout_seconds: int = 15,
    retry_on: Optional[str] = None,
    num_retries: int = 1,
    header_matches: Optional[List[dict]] = None,
) -> List[RouteEntry]:
    """Build a list of RouteEntry objects for a given cluster."""
    if not cluster:
        raise RouteError("cluster name must not be empty")
    if not prefix.startswith("/"):
        raise RouteError(f"prefix must start with '/': got '{prefix}'")
    if timeout_seconds <= 0:
        raise RouteError("timeout_seconds must be positive")

    match = RouteMatch(
        prefix=prefix,
        headers=header_matches or [],
    )
    action = RouteAction(
        cluster=cluster,
        timeout_seconds=timeout_seconds,
        retry_on=retry_on,
        num_retries=num_retries,
    )
    return [RouteEntry(match=match, action=action)]


def routes_to_envoy_list(routes: List[RouteEntry]) -> List[dict]:
    """Serialize a list of RouteEntry objects to Envoy-compatible dicts."""
    return [r.to_envoy_dict() for r in routes]

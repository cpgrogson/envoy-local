"""Summarizer: produce human-readable summaries of EnvoyConfig objects."""

from dataclasses import dataclass, field
from typing import List

from envoy_local.config import EnvoyConfig


@dataclass
class SummaryLine:
    label: str
    value: str

    def __str__(self) -> str:
        return f"  {self.label:<28} {self.value}"


@dataclass
class ConfigSummary:
    lines: List[SummaryLine] = field(default_factory=list)

    def add(self, label: str, value: str) -> None:
        self.lines.append(SummaryLine(label, value))

    def __str__(self) -> str:
        header = "=== Envoy Config Summary ==="
        body = "\n".join(str(line) for line in self.lines)
        return f"{header}\n{body}"

    def as_dict(self) -> dict:
        return {line.label: line.value for line in self.lines}


def summarize(config: EnvoyConfig) -> ConfigSummary:
    """Build a ConfigSummary from an EnvoyConfig instance."""
    summary = ConfigSummary()

    summary.add("Listener port", str(config.listener.port))
    summary.add("Admin port", str(config.admin_port))

    upstream_count = len(config.upstreams)
    summary.add("Upstream count", str(upstream_count))

    if upstream_count == 0:
        summary.add("Upstreams", "(none)")
    else:
        names = ", ".join(u.name for u in config.upstreams)
        summary.add("Upstreams", names)

        hosts = ", ".join(f"{u.host}:{u.port}" for u in config.upstreams)
        summary.add("Upstream addresses", hosts)

    route_prefix = config.listener.route_prefix if hasattr(config.listener, "route_prefix") else "/"
    summary.add("Route prefix", str(route_prefix))

    return summary

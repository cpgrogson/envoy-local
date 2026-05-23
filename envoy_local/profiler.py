"""Config profiler: analyzes an EnvoyConfig and reports performance hints."""

from dataclasses import dataclass, field
from typing import List

from envoy_local.config import EnvoyConfig


@dataclass
class ProfileHint:
    level: str  # 'info', 'warning', 'critical'
    message: str

    def __str__(self) -> str:
        return f"[{self.level.upper()}] {self.message}"


@dataclass
class ProfileReport:
    hints: List[ProfileHint] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        return any(h.level in ("warning", "critical") for h in self.hints)

    @property
    def critical_count(self) -> int:
        return sum(1 for h in self.hints if h.level == "critical")

    def summary(self) -> str:
        if not self.hints:
            return "No issues found."
        lines = [str(h) for h in self.hints]
        lines.append(
            f"Total: {len(self.hints)} hint(s), {self.critical_count} critical."
        )
        return "\n".join(lines)


def profile_config(config: EnvoyConfig) -> ProfileReport:
    """Analyze *config* and return a :class:`ProfileReport` with hints."""
    hints: List[ProfileHint] = []

    # Listener port checks
    for listener in config.listeners:
        if listener.port < 1024:
            hints.append(
                ProfileHint(
                    "warning",
                    f"Listener on port {listener.port} is a privileged port (<1024).",
                )
            )

    # Upstream / cluster checks
    all_upstreams = [
        upstream
        for listener in config.listeners
        for upstream in listener.upstreams
    ]

    if not all_upstreams:
        hints.append(
            ProfileHint("warning", "No upstream services defined; proxy has nothing to route to.")
        )

    seen_addresses = set()
    for upstream in all_upstreams:
        addr = (upstream.address, upstream.port)
        if addr in seen_addresses:
            hints.append(
                ProfileHint(
                    "warning",
                    f"Duplicate upstream address {upstream.address}:{upstream.port} detected.",
                )
            )
        seen_addresses.add(addr)

        if upstream.port < 1:
            hints.append(
                ProfileHint("critical", f"Upstream '{upstream.name}' has invalid port {upstream.port}.")
            )

    # Admin port checks
    if config.admin_port == 0:
        hints.append(ProfileHint("critical", "Admin port is 0; admin interface will be disabled."))

    return ProfileReport(hints=hints)

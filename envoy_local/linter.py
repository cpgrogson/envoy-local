"""Linter for Envoy local config — checks for common misconfigurations and style issues."""

from dataclasses import dataclass, field
from typing import List
from envoy_local.config import EnvoyConfig


@dataclass
class LintIssue:
    level: str  # 'warning' or 'error'
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.level.upper()}] {self.code}: {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.level == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.level == "warning" for i in self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.level == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.level == "warning")

    def __str__(self) -> str:
        if not self.issues:
            return "Lint passed: no issues found."
        lines = [str(i) for i in self.issues]
        lines.append(f"{self.error_count} error(s), {self.warning_count} warning(s).")
        return "\n".join(lines)


def lint_config(config: EnvoyConfig) -> LintResult:
    """Run all lint checks against an EnvoyConfig and return a LintResult."""
    result = LintResult()

    # Check for duplicate upstream names
    names = [u.name for u in config.upstreams]
    seen = set()
    for name in names:
        if name in seen:
            result.issues.append(LintIssue(
                level="error",
                code="DUPLICATE_UPSTREAM",
                message=f"Upstream name '{name}' is defined more than once.",
            ))
        seen.add(name)

    # Check for upstreams using the same host:port
    addresses = [(u.host, u.port) for u in config.upstreams]
    seen_addrs: dict = {}
    for upstream in config.upstreams:
        addr = (upstream.host, upstream.port)
        if addr in seen_addrs:
            result.issues.append(LintIssue(
                level="warning",
                code="DUPLICATE_ADDRESS",
                message=(
                    f"Upstream '{upstream.name}' shares address "
                    f"{upstream.host}:{upstream.port} with '{seen_addrs[addr]}'."
                ),
            ))
        else:
            seen_addrs[addr] = upstream.name

    # Warn if listener port and admin port are the same
    for listener in config.listeners:
        if listener.port == config.admin_port:
            result.issues.append(LintIssue(
                level="error",
                code="PORT_CONFLICT",
                message=(
                    f"Listener port {listener.port} conflicts with admin port {config.admin_port}."
                ),
            ))

    # Warn if no upstreams are defined
    if not config.upstreams:
        result.issues.append(LintIssue(
            level="warning",
            code="NO_UPSTREAMS",
            message="No upstream services defined; generated config will have no clusters.",
        ))

    return result

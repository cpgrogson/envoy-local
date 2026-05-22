"""Validates EnvoyConfig objects before rendering or writing."""

from dataclasses import dataclass
from typing import List

from envoy_local.config import EnvoyConfig


@dataclass
class ValidationError:
    field: str
    message: str

    def __str__(self) -> str:
        return f"[{self.field}] {self.message}"


@dataclass
class ValidationResult:
    errors: List[ValidationError]

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def __str__(self) -> str:
        if self.is_valid:
            return "Config is valid."
        return "Validation failed:\n" + "\n".join(f"  - {e}" for e in self.errors)


def validate(config: EnvoyConfig) -> ValidationResult:
    """Run all validation checks on an EnvoyConfig and return a ValidationResult."""
    errors: List[ValidationError] = []

    _check_ports(config, errors)
    _check_admin(config, errors)
    _check_upstreams(config, errors)

    return ValidationResult(errors=errors)


def _check_ports(config: EnvoyConfig, errors: List[ValidationError]) -> None:
    if not (1 <= config.listener.port <= 65535):
        errors.append(ValidationError("listener.port", f"Port {config.listener.port} is out of valid range (1-65535)."))

    if not (1 <= config.admin_port <= 65535):
        errors.append(ValidationError("admin_port", f"Admin port {config.admin_port} is out of valid range (1-65535)."))

    if config.listener.port == config.admin_port:
        errors.append(ValidationError("ports", "Listener port and admin port must not be the same."))


def _check_admin(config: EnvoyConfig, errors: List[ValidationError]) -> None:
    if not config.admin_address:
        errors.append(ValidationError("admin_address", "Admin address must not be empty."))


def _check_upstreams(config: EnvoyConfig, errors: List[ValidationError]) -> None:
    seen_names: set = set()
    for i, upstream in enumerate(config.upstreams):
        prefix = f"upstreams[{i}]"

        if not upstream.name:
            errors.append(ValidationError(f"{prefix}.name", "Upstream name must not be empty."))

        if upstream.name in seen_names:
            errors.append(ValidationError(f"{prefix}.name", f"Duplicate upstream name '{upstream.name}'."))
        seen_names.add(upstream.name)

        if not upstream.host:
            errors.append(ValidationError(f"{prefix}.host", "Upstream host must not be empty."))

        if not (1 <= upstream.port <= 65535):
            errors.append(ValidationError(f"{prefix}.port", f"Port {upstream.port} is out of valid range (1-65535)."))

"""Template-based config generation for common Envoy proxy patterns."""

from dataclasses import dataclass
from typing import List, Optional

from envoy_local.config import EnvoyConfig, ListenerConfig, UpstreamService, add_upstream


class TemplateError(Exception):
    """Raised when a template cannot be applied."""
    pass


@dataclass
class TemplateResult:
    template_name: str
    config: EnvoyConfig

    def __str__(self) -> str:
        return f"TemplateResult(template={self.template_name!r}, listener={self.config.listener.port})"


def _base_config(listener_port: int, admin_port: int) -> EnvoyConfig:
    return EnvoyConfig(
        listener=ListenerConfig(port=listener_port),
        admin_port=admin_port,
        upstreams=[],
    )


def apply_template(name: str, **kwargs) -> TemplateResult:
    """Apply a named template and return a TemplateResult.

    Supported templates:
      - 'sidecar': single upstream, standard sidecar pattern
      - 'egress-gateway': multiple upstreams behind one listener
    """
    if name == "sidecar":
        return _apply_sidecar(**kwargs)
    elif name == "egress-gateway":
        return _apply_egress_gateway(**kwargs)
    else:
        raise TemplateError(f"Unknown template: {name!r}")


def _apply_sidecar(
    upstream_host: str,
    upstream_port: int,
    listener_port: int = 10000,
    admin_port: int = 9901,
    upstream_name: Optional[str] = None,
) -> TemplateResult:
    if not upstream_host:
        raise TemplateError("sidecar template requires 'upstream_host'")
    if not (1 <= upstream_port <= 65535):
        raise TemplateError("sidecar template requires a valid 'upstream_port'")

    name = upstream_name or upstream_host.replace(".", "_")
    cfg = _base_config(listener_port, admin_port)
    upstream = UpstreamService(name=name, host=upstream_host, port=upstream_port)
    cfg = add_upstream(cfg, upstream)
    return TemplateResult(template_name="sidecar", config=cfg)


def _apply_egress_gateway(
    upstreams: List[dict],
    listener_port: int = 10000,
    admin_port: int = 9901,
) -> TemplateResult:
    if not upstreams:
        raise TemplateError("egress-gateway template requires at least one upstream")

    cfg = _base_config(listener_port, admin_port)
    for entry in upstreams:
        try:
            svc = UpstreamService(
                name=entry["name"],
                host=entry["host"],
                port=int(entry["port"]),
            )
        except KeyError as exc:
            raise TemplateError(f"Upstream entry missing field: {exc}") from exc
        cfg = add_upstream(cfg, svc)
    return TemplateResult(template_name="egress-gateway", config=cfg)

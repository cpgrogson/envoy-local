"""Merge multiple EnvoyConfig objects into a single unified config."""

from dataclasses import dataclass, field
from typing import List, Optional

from envoy_local.config import EnvoyConfig, UpstreamService, ListenerConfig, add_upstream


class MergeError(Exception):
    """Raised when configs cannot be merged."""
    pass


@dataclass
class MergeResult:
    config: EnvoyConfig
    merged_count: int
    skipped_upstreams: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        parts = [f"Merged {self.merged_count} config(s)"]
        if self.skipped_upstreams:
            parts.append(f"skipped duplicates: {', '.join(self.skipped_upstreams)}")
        return "; ".join(parts)


def merge_configs(configs: List[EnvoyConfig], base: Optional[EnvoyConfig] = None) -> MergeResult:
    """Merge a list of EnvoyConfig objects into one.

    The first config (or base) provides the listener and admin settings.
    Upstreams from all configs are merged; duplicates by name are skipped.
    """
    if not configs:
        raise MergeError("No configs provided to merge")

    source = base if base is not None else configs[0]
    result = EnvoyConfig(
        listener=ListenerConfig(
            port=source.listener.port,
            routes=list(source.listener.routes),
        ),
        admin_port=source.admin_port,
        upstreams=list(source.upstreams),
    )

    seen_names = {u.name for u in result.upstreams}
    skipped: List[str] = []

    start_index = 0 if base is not None else 1
    for cfg in configs[start_index:]:
        for upstream in cfg.upstreams:
            if upstream.name in seen_names:
                skipped.append(upstream.name)
            else:
                seen_names.add(upstream.name)
                result = add_upstream(result, upstream)

    return MergeResult(
        config=result,
        merged_count=len(configs),
        skipped_upstreams=skipped,
    )

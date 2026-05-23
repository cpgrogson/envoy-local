"""Snapshot management for Envoy local configs."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

from envoy_local.config import EnvoyConfig
from envoy_local.renderer import render


@dataclass
class ConfigSnapshot:
    """Immutable record of a rendered Envoy configuration at a point in time."""

    config: EnvoyConfig
    rendered_yaml: str
    checksum: str = field(init=False)
    timestamp: str = field(init=False)

    def __post_init__(self) -> None:
        self.checksum = hashlib.sha256(self.rendered_yaml.encode()).hexdigest()[:16]
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checksum": self.checksum,
            "timestamp": self.timestamp,
            "admin_port": self.config.admin_port,
            "listener": {
                "port": self.config.listener.port,
                "route_prefix": self.config.listener.route_prefix,
            },
            "upstreams": [
                {
                    "name": u.name,
                    "host": u.host,
                    "port": u.port,
                }
                for u in self.config.upstreams
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], rendered_yaml: str = "") -> "ConfigSnapshot":
        from envoy_local.config import ListenerConfig, UpstreamService

        upstreams = [
            UpstreamService(name=u["name"], host=u["host"], port=u["port"])
            for u in data.get("upstreams", [])
        ]
        listener = ListenerConfig(
            port=data["listener"]["port"],
            route_prefix=data["listener"].get("route_prefix", "/"),
        )
        config = EnvoyConfig(
            listener=listener,
            admin_port=data["admin_port"],
            upstreams=upstreams,
        )
        snap = cls(config=config, rendered_yaml=rendered_yaml or render(config))
        snap.checksum = data.get("checksum", snap.checksum)
        snap.timestamp = data.get("timestamp", snap.timestamp)
        return snap

    @classmethod
    def from_config(cls, config: EnvoyConfig) -> "ConfigSnapshot":
        return cls(config=config, rendered_yaml=render(config))


def save_snapshot(snapshot: ConfigSnapshot, directory: str = ".") -> str:
    """Persist a snapshot as JSON and return the file path."""
    os.makedirs(directory, exist_ok=True)
    filename = f"snapshot_{snapshot.checksum}.json"
    path = os.path.join(directory, filename)
    with open(path, "w") as fh:
        json.dump(snapshot.to_dict(), fh, indent=2)
    return path


def load_snapshot(path: str) -> ConfigSnapshot:
    """Load a snapshot from a JSON file."""
    with open(path) as fh:
        data = json.load(fh)
    return ConfigSnapshot.from_dict(data)

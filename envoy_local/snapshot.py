"""Snapshot management for saving and comparing Envoy config states."""

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ConfigSnapshot:
    """Represents a point-in-time snapshot of a rendered Envoy config."""

    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    checksum: str = field(init=False)

    def __post_init__(self):
        self.checksum = hashlib.sha256(self.content.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "checksum": self.checksum,
            "content": self.content,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConfigSnapshot":
        snap = cls(content=data["content"], timestamp=data["timestamp"])
        return snap


def save_snapshot(snapshot: ConfigSnapshot, path: str) -> None:
    """Persist a snapshot to a JSON file."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(snapshot.to_dict(), f, indent=2)


def load_snapshot(path: str) -> Optional[ConfigSnapshot]:
    """Load a snapshot from a JSON file. Returns None if file does not exist."""
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        data = json.load(f)
    return ConfigSnapshot.from_dict(data)


def has_changed(current: ConfigSnapshot, previous: Optional[ConfigSnapshot]) -> bool:
    """Return True if the current snapshot differs from the previous one."""
    if previous is None:
        return True
    return current.checksum != previous.checksum

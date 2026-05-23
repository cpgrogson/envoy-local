"""Diff utilities for comparing Envoy config snapshots."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Tuple

from envoy_local.snapshot import ConfigSnapshot


@dataclass
class DiffEntry:
    """Represents a single difference between two snapshots."""

    path: str
    old_value: object
    new_value: object

    def __str__(self) -> str:
        return f"  {self.path}: {self.old_value!r} -> {self.new_value!r}"


@dataclass
class SnapshotDiff:
    """Result of comparing two ConfigSnapshots."""

    old_checksum: str
    new_checksum: str
    entries: List[DiffEntry]

    @property
    def has_changes(self) -> bool:
        return len(self.entries) > 0

    def summary(self) -> str:
        if not self.has_changes:
            return "No changes detected."
        lines = [
            f"Changes ({len(self.entries)}):",
            f"  checksum: {self.old_checksum} -> {self.new_checksum}",
        ]
        lines.extend(str(e) for e in self.entries)
        return "\n".join(lines)


def _flatten(obj: object, prefix: str = "") -> List[Tuple[str, object]]:
    """Recursively flatten a nested dict/list into (dotted.path, value) pairs."""
    items: List[Tuple[str, object]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            items.extend(_flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            items.extend(_flatten(v, f"{prefix}[{i}]"))
    else:
        items.append((prefix, obj))
    return items


def diff_snapshots(old: ConfigSnapshot, new: ConfigSnapshot) -> SnapshotDiff:
    """Compare two snapshots and return a SnapshotDiff describing changes."""
    old_flat = dict(_flatten(old.to_dict()))
    new_flat = dict(_flatten(new.to_dict()))

    all_keys = set(old_flat) | set(new_flat)
    entries: List[DiffEntry] = []

    for key in sorted(all_keys):
        old_val = old_flat.get(key)
        new_val = new_flat.get(key)
        if old_val != new_val:
            entries.append(DiffEntry(path=key, old_value=old_val, new_value=new_val))

    return SnapshotDiff(
        old_checksum=old.checksum,
        new_checksum=new.checksum,
        entries=entries,
    )

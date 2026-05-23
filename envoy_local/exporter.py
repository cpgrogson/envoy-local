"""Export ConfigSnapshot to various output formats (JSON, YAML, summary text)."""

from __future__ import annotations

import json
import os
from typing import Optional

import yaml

from envoy_local.snapshot import ConfigSnapshot


SUPPORTED_FORMATS = ("json", "yaml", "summary")


class ExportError(Exception):
    """Raised when an export operation fails."""


def export_snapshot(snapshot: ConfigSnapshot, fmt: str, output_path: Optional[str] = None) -> str:
    """Serialize *snapshot* to *fmt* and optionally write to *output_path*.

    Returns the serialized string regardless of whether a file was written.

    Raises ExportError for unsupported formats or I/O failures.
    """
    fmt = fmt.lower()
    if fmt not in SUPPORTED_FORMATS:
        raise ExportError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    if fmt == "json":
        content = _to_json(snapshot)
    elif fmt == "yaml":
        content = _to_yaml(snapshot)
    else:
        content = _to_summary(snapshot)

    if output_path:
        _write(output_path, content)

    return content


def _to_json(snapshot: ConfigSnapshot) -> str:
    return json.dumps(snapshot.to_dict(), indent=2)


def _to_yaml(snapshot: ConfigSnapshot) -> str:
    return yaml.dump(snapshot.to_dict(), default_flow_style=False, sort_keys=False)


def _to_summary(snapshot: ConfigSnapshot) -> str:
    d = snapshot.to_dict()
    lines = [
        f"Snapshot ID : {snapshot.snapshot_id}",
        f"Timestamp   : {snapshot.timestamp}",
        f"Checksum    : {snapshot.checksum}",
        f"Listener    : 0.0.0.0:{d.get('listener_port', '?')}",
        f"Admin       : 0.0.0.0:{d.get('admin_port', '?')}",
        "Upstreams   :",
    ]
    for up in d.get("upstreams", []):
        lines.append(f"  - {up.get('name')}  {up.get('host')}:{up.get('port')}")
    return "\n".join(lines)


def _write(path: str, content: str) -> None:
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
    except OSError as exc:
        raise ExportError(f"Failed to write export to '{path}': {exc}") from exc

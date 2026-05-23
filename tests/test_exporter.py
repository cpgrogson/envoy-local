"""Tests for envoy_local.exporter."""

import json
import os

import pytest
import yaml

from envoy_local.config import EnvoyConfig, ListenerConfig, UpstreamService
from envoy_local.exporter import ExportError, export_snapshot, SUPPORTED_FORMATS
from envoy_local.snapshot import ConfigSnapshot


@pytest.fixture()
def snapshot():
    cfg = EnvoyConfig(
        listener=ListenerConfig(port=8080, admin_port=9901),
        upstreams=[
            UpstreamService(name="svc-a", host="127.0.0.1", port=5000),
            UpstreamService(name="svc-b", host="127.0.0.1", port=5001),
        ],
    )
    return ConfigSnapshot.from_config(cfg)


def test_export_json_returns_valid_json(snapshot):
    result = export_snapshot(snapshot, "json")
    parsed = json.loads(result)
    assert parsed["listener_port"] == 8080


def test_export_yaml_returns_valid_yaml(snapshot):
    result = export_snapshot(snapshot, "yaml")
    parsed = yaml.safe_load(result)
    assert parsed["admin_port"] == 9901


def test_export_summary_contains_key_fields(snapshot):
    result = export_snapshot(snapshot, "summary")
    assert "Snapshot ID" in result
    assert "svc-a" in result
    assert "svc-b" in result
    assert "8080" in result


def test_export_unsupported_format_raises(snapshot):
    with pytest.raises(ExportError, match="Unsupported format"):
        export_snapshot(snapshot, "xml")


def test_export_writes_file(snapshot, tmp_path):
    out = tmp_path / "out" / "snap.json"
    export_snapshot(snapshot, "json", output_path=str(out))
    assert out.exists()
    data = json.loads(out.read_text())
    assert "checksum" in data


def test_export_yaml_writes_file(snapshot, tmp_path):
    out = tmp_path / "snap.yaml"
    export_snapshot(snapshot, "yaml", output_path=str(out))
    assert out.exists()


def test_export_returns_content_even_when_writing(snapshot, tmp_path):
    out = tmp_path / "snap.json"
    content = export_snapshot(snapshot, "json", output_path=str(out))
    assert isinstance(content, str)
    assert len(content) > 0


def test_export_upstreams_in_json(snapshot):
    result = json.loads(export_snapshot(snapshot, "json"))
    names = [u["name"] for u in result["upstreams"]]
    assert "svc-a" in names
    assert "svc-b" in names


def test_supported_formats_constant():
    assert "json" in SUPPORTED_FORMATS
    assert "yaml" in SUPPORTED_FORMATS
    assert "summary" in SUPPORTED_FORMATS


def test_export_write_failure_raises_export_error(snapshot):
    with pytest.raises(ExportError, match="Failed to write"):
        # Root-level path that cannot be created on most systems
        export_snapshot(snapshot, "json", output_path="/no_such_dir/sub/file.json")

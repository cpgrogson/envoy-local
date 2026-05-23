"""Tests for envoy_local.differ."""

import pytest

from envoy_local.config import EnvoyConfig, ListenerConfig, UpstreamService
from envoy_local.snapshot import ConfigSnapshot
from envoy_local.differ import DiffEntry, SnapshotDiff, diff_snapshots, _flatten


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_config(listener_port: int = 8080, admin_port: int = 9901) -> EnvoyConfig:
    cfg = EnvoyConfig(
        listener=ListenerConfig(port=listener_port),
        admin_port=admin_port,
    )
    return cfg


@pytest.fixture
def snap_a() -> ConfigSnapshot:
    return ConfigSnapshot.from_config(_make_config(listener_port=8080))


@pytest.fixture
def snap_b() -> ConfigSnapshot:
    return ConfigSnapshot.from_config(_make_config(listener_port=9090))


# ---------------------------------------------------------------------------
# _flatten
# ---------------------------------------------------------------------------

def test_flatten_simple_dict():
    result = dict(_flatten({"a": 1, "b": 2}))
    assert result == {"a": 1, "b": 2}


def test_flatten_nested_dict():
    result = dict(_flatten({"a": {"b": {"c": 42}}}))
    assert result == {"a.b.c": 42}


def test_flatten_list():
    result = dict(_flatten({"items": [10, 20]}))
    assert result["items[0]"] == 10
    assert result["items[1]"] == 20


# ---------------------------------------------------------------------------
# diff_snapshots — identical configs
# ---------------------------------------------------------------------------

def test_diff_identical_snapshots_no_changes(snap_a):
    snap_a2 = ConfigSnapshot.from_config(_make_config(listener_port=8080))
    result = diff_snapshots(snap_a, snap_a2)
    # checksums may differ due to timestamps; check entries only
    # Filter out timestamp/checksum entries from entries list
    non_meta = [e for e in result.entries if "timestamp" not in e.path and "checksum" not in e.path]
    assert non_meta == []


# ---------------------------------------------------------------------------
# diff_snapshots — changed listener port
# ---------------------------------------------------------------------------

def test_diff_detects_listener_port_change(snap_a, snap_b):
    result = diff_snapshots(snap_a, snap_b)
    paths = [e.path for e in result.entries]
    assert any("port" in p for p in paths)


def test_diff_has_changes_true_when_entries_present(snap_a, snap_b):
    result = diff_snapshots(snap_a, snap_b)
    assert result.has_changes


def test_diff_checksums_recorded(snap_a, snap_b):
    result = diff_snapshots(snap_a, snap_b)
    assert result.old_checksum == snap_a.checksum
    assert result.new_checksum == snap_b.checksum


# ---------------------------------------------------------------------------
# SnapshotDiff.summary
# ---------------------------------------------------------------------------

def test_summary_no_changes():
    diff = SnapshotDiff(old_checksum="abc", new_checksum="abc", entries=[])
    assert diff.summary() == "No changes detected."


def test_summary_with_changes(snap_a, snap_b):
    result = diff_snapshots(snap_a, snap_b)
    summary = result.summary()
    assert "Changes" in summary
    assert "->"
    in summary


def test_diff_entry_str():
    entry = DiffEntry(path="listener.port", old_value=8080, new_value=9090)
    assert "listener.port" in str(entry)
    assert "8080" in str(entry)
    assert "9090" in str(entry)

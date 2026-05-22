"""Tests for envoy_local.snapshot module."""

import json
import os
import pytest

from envoy_local.snapshot import (
    ConfigSnapshot,
    has_changed,
    load_snapshot,
    save_snapshot,
)

SAMPLE_CONTENT = "static_resources:\n  clusters: []\n"


@pytest.fixture
def snapshot():
    return ConfigSnapshot(content=SAMPLE_CONTENT)


def test_snapshot_checksum_is_set(snapshot):
    assert snapshot.checksum is not None
    assert len(snapshot.checksum) == 64  # SHA-256 hex digest


def test_snapshot_timestamp_is_set(snapshot):
    assert snapshot.timestamp is not None
    assert "T" in snapshot.timestamp  # ISO format


def test_snapshot_to_dict(snapshot):
    d = snapshot.to_dict()
    assert d["content"] == SAMPLE_CONTENT
    assert d["checksum"] == snapshot.checksum
    assert d["timestamp"] == snapshot.timestamp


def test_snapshot_from_dict_roundtrip(snapshot):
    restored = ConfigSnapshot.from_dict(snapshot.to_dict())
    assert restored.content == snapshot.content
    assert restored.checksum == snapshot.checksum
    assert restored.timestamp == snapshot.timestamp


def test_same_content_produces_same_checksum():
    s1 = ConfigSnapshot(content=SAMPLE_CONTENT)
    s2 = ConfigSnapshot(content=SAMPLE_CONTENT)
    assert s1.checksum == s2.checksum


def test_different_content_produces_different_checksum():
    s1 = ConfigSnapshot(content=SAMPLE_CONTENT)
    s2 = ConfigSnapshot(content=SAMPLE_CONTENT + "\n")
    assert s1.checksum != s2.checksum


def test_save_and_load_snapshot(tmp_path):
    snap = ConfigSnapshot(content=SAMPLE_CONTENT)
    path = str(tmp_path / "snap.json")
    save_snapshot(snap, path)
    assert os.path.exists(path)
    loaded = load_snapshot(path)
    assert loaded is not None
    assert loaded.checksum == snap.checksum
    assert loaded.content == snap.content


def test_load_snapshot_returns_none_for_missing_file(tmp_path):
    result = load_snapshot(str(tmp_path / "nonexistent.json"))
    assert result is None


def test_has_changed_when_no_previous(snapshot):
    assert has_changed(snapshot, None) is True


def test_has_changed_when_identical(snapshot):
    previous = ConfigSnapshot(content=SAMPLE_CONTENT)
    assert has_changed(snapshot, previous) is False


def test_has_changed_when_different(snapshot):
    previous = ConfigSnapshot(content="different: content\n")
    assert has_changed(snapshot, previous) is True

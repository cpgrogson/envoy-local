"""Tests for envoy_local.watcher."""

import time
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envoy_local.watcher import ConfigWatcher


@pytest.fixture
def tmp_source(tmp_path):
    f = tmp_path / "config.yaml"
    f.write_text("initial: true\n")
    return f


def test_watcher_calls_callback_on_change(tmp_source):
    callback = MagicMock()
    watcher = ConfigWatcher(str(tmp_source), on_change=callback, poll_interval=0.05)

    # Prime the watcher with the initial mtime
    watcher._last_mtime = None
    watcher._check_and_trigger()  # sets _last_mtime, no callback yet

    # Modify the file
    time.sleep(0.05)
    tmp_source.write_text("updated: true\n")

    changed = watcher._check_and_trigger()
    assert changed
    callback.assert_called_once_with(str(tmp_source))


def test_watcher_no_callback_when_unchanged(tmp_source):
    callback = MagicMock()
    watcher = ConfigWatcher(str(tmp_source), on_change=callback, poll_interval=0.05)
    watcher._last_mtime = None
    watcher._check_and_trigger()  # initialise

    changed = watcher._check_and_trigger()  # no change
    assert not changed
    callback.assert_not_called()


def test_watcher_handles_missing_file():
    callback = MagicMock()
    watcher = ConfigWatcher("/nonexistent/path.yaml", on_change=callback)
    watcher._last_mtime = 12345.0
    result = watcher._check_and_trigger()
    assert not result
    callback.assert_not_called()


def test_watcher_stop_ends_loop(tmp_source):
    callback = MagicMock()
    watcher = ConfigWatcher(str(tmp_source), on_change=callback, poll_interval=0.05)

    thread = threading.Thread(target=watcher.start)
    thread.start()
    time.sleep(0.15)
    watcher.stop()
    thread.join(timeout=1.0)

    assert not thread.is_alive()
    assert not watcher._running


def test_watcher_running_flag_false_after_stop(tmp_source):
    callback = MagicMock()
    watcher = ConfigWatcher(str(tmp_source), on_change=callback, poll_interval=0.05)
    assert not watcher._running
    watcher.stop()
    assert not watcher._running


def test_watcher_poll_interval_default():
    watcher = ConfigWatcher("some/path.yaml", on_change=lambda p: None)
    assert watcher.poll_interval == 1.0

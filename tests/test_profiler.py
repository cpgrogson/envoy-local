"""Tests for envoy_local.profiler."""

import pytest

from envoy_local.config import EnvoyConfig, ListenerConfig, UpstreamService
from envoy_local.profiler import ProfileHint, ProfileReport, profile_config


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def clean_config():
    upstream = UpstreamService(name="backend", address="127.0.0.1", port=8080)
    listener = ListenerConfig(port=10000, upstreams=[upstream])
    return EnvoyConfig(listeners=[listener], admin_port=9901)


# ---------------------------------------------------------------------------
# ProfileHint
# ---------------------------------------------------------------------------


def test_hint_str_format():
    hint = ProfileHint(level="warning", message="something fishy")
    assert str(hint) == "[WARNING] something fishy"


def test_hint_critical_str():
    hint = ProfileHint(level="critical", message="bad port")
    assert "CRITICAL" in str(hint)


# ---------------------------------------------------------------------------
# ProfileReport
# ---------------------------------------------------------------------------


def test_report_no_hints_has_no_warnings():
    report = ProfileReport()
    assert not report.has_warnings


def test_report_with_warning_has_warnings():
    report = ProfileReport(hints=[ProfileHint("warning", "test")])
    assert report.has_warnings


def test_report_critical_count():
    hints = [
        ProfileHint("info", "a"),
        ProfileHint("critical", "b"),
        ProfileHint("critical", "c"),
    ]
    report = ProfileReport(hints=hints)
    assert report.critical_count == 2


def test_report_summary_no_issues():
    report = ProfileReport()
    assert report.summary() == "No issues found."


def test_report_summary_contains_hints():
    report = ProfileReport(hints=[ProfileHint("warning", "watch out")])
    summary = report.summary()
    assert "watch out" in summary
    assert "1 hint" in summary


# ---------------------------------------------------------------------------
# profile_config
# ---------------------------------------------------------------------------


def test_clean_config_no_warnings(clean_config):
    report = profile_config(clean_config)
    assert not report.has_warnings


def test_privileged_port_triggers_warning():
    upstream = UpstreamService(name="svc", address="127.0.0.1", port=8080)
    listener = ListenerConfig(port=80, upstreams=[upstream])
    config = EnvoyConfig(listeners=[listener], admin_port=9901)
    report = profile_config(config)
    assert any("privileged" in h.message for h in report.hints)


def test_no_upstreams_triggers_warning():
    listener = ListenerConfig(port=10000, upstreams=[])
    config = EnvoyConfig(listeners=[listener], admin_port=9901)
    report = profile_config(config)
    assert any("nothing to route" in h.message for h in report.hints)


def test_duplicate_upstream_triggers_warning():
    upstream_a = UpstreamService(name="a", address="127.0.0.1", port=8080)
    upstream_b = UpstreamService(name="b", address="127.0.0.1", port=8080)
    listener = ListenerConfig(port=10000, upstreams=[upstream_a, upstream_b])
    config = EnvoyConfig(listeners=[listener], admin_port=9901)
    report = profile_config(config)
    assert any("Duplicate" in h.message for h in report.hints)


def test_admin_port_zero_is_critical():
    upstream = UpstreamService(name="svc", address="127.0.0.1", port=8080)
    listener = ListenerConfig(port=10000, upstreams=[upstream])
    config = EnvoyConfig(listeners=[listener], admin_port=0)
    report = profile_config(config)
    assert report.critical_count >= 1
    assert any("Admin port" in h.message for h in report.hints)

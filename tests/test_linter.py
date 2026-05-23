"""Tests for envoy_local.linter."""

import pytest
from envoy_local.config import EnvoyConfig, ListenerConfig, UpstreamService
from envoy_local.linter import lint_config, LintIssue, LintResult


def _make_config(
    upstreams=None,
    admin_port=9901,
    listener_port=10000,
) -> EnvoyConfig:
    listeners = [ListenerConfig(port=listener_port)]
    return EnvoyConfig(
        listeners=listeners,
        upstreams=upstreams or [],
        admin_port=admin_port,
    )


@pytest.fixture
def clean_config():
    return _make_config(
        upstreams=[
            UpstreamService(name="svc-a", host="127.0.0.1", port=8080),
            UpstreamService(name="svc-b", host="127.0.0.1", port=8081),
        ]
    )


def test_clean_config_has_no_issues(clean_config):
    result = lint_config(clean_config)
    assert not result.has_errors
    assert not result.has_warnings
    assert result.issues == []


def test_lint_result_str_no_issues(clean_config):
    result = lint_config(clean_config)
    assert "no issues" in str(result)


def test_duplicate_upstream_name_is_error():
    config = _make_config(upstreams=[
        UpstreamService(name="svc-a", host="127.0.0.1", port=8080),
        UpstreamService(name="svc-a", host="127.0.0.1", port=8082),
    ])
    result = lint_config(config)
    assert result.has_errors
    codes = [i.code for i in result.issues]
    assert "DUPLICATE_UPSTREAM" in codes


def test_duplicate_address_is_warning():
    config = _make_config(upstreams=[
        UpstreamService(name="svc-a", host="127.0.0.1", port=8080),
        UpstreamService(name="svc-b", host="127.0.0.1", port=8080),
    ])
    result = lint_config(config)
    assert result.has_warnings
    codes = [i.code for i in result.issues]
    assert "DUPLICATE_ADDRESS" in codes


def test_port_conflict_between_listener_and_admin():
    config = _make_config(admin_port=9901, listener_port=9901)
    result = lint_config(config)
    assert result.has_errors
    codes = [i.code for i in result.issues]
    assert "PORT_CONFLICT" in codes


def test_no_upstreams_is_warning():
    config = _make_config(upstreams=[])
    result = lint_config(config)
    assert result.has_warnings
    codes = [i.code for i in result.issues]
    assert "NO_UPSTREAMS" in codes


def test_error_and_warning_counts():
    config = _make_config(
        upstreams=[
            UpstreamService(name="svc-a", host="127.0.0.1", port=8080),
            UpstreamService(name="svc-a", host="127.0.0.1", port=8081),  # duplicate name
        ],
        admin_port=9901,
        listener_port=9901,  # port conflict
    )
    result = lint_config(config)
    assert result.error_count >= 2


def test_lint_issue_str_format():
    issue = LintIssue(level="warning", code="NO_UPSTREAMS", message="No upstreams defined.")
    s = str(issue)
    assert "WARNING" in s
    assert "NO_UPSTREAMS" in s
    assert "No upstreams defined." in s


def test_lint_result_str_with_issues():
    config = _make_config(upstreams=[])
    result = lint_config(config)
    s = str(result)
    assert "warning" in s.lower() or "Warning" in s

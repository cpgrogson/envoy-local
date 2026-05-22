"""Tests for envoy_local.validator module."""

import pytest

from envoy_local.config import EnvoyConfig, ListenerConfig, UpstreamService
from envoy_local.validator import validate, ValidationResult


@pytest.fixture
def valid_config() -> EnvoyConfig:
    return EnvoyConfig(
        listener=ListenerConfig(port=8080),
        admin_port=9901,
        admin_address="127.0.0.1",
        upstreams=[
            UpstreamService(name="auth", host="auth-service", port=5000),
            UpstreamService(name="users", host="users-service", port=5001),
        ],
    )


def test_valid_config_passes(valid_config):
    result = validate(valid_config)
    assert result.is_valid
    assert result.errors == []


def test_str_valid(valid_config):
    result = validate(valid_config)
    assert str(result) == "Config is valid."


def test_listener_port_zero_is_invalid(valid_config):
    valid_config.listener.port = 0
    result = validate(valid_config)
    assert not result.is_valid
    assert any("listener.port" in e.field for e in result.errors)


def test_admin_port_out_of_range(valid_config):
    valid_config.admin_port = 99999
    result = validate(valid_config)
    assert not result.is_valid
    assert any("admin_port" in e.field for e in result.errors)


def test_same_listener_and_admin_port(valid_config):
    valid_config.admin_port = valid_config.listener.port
    result = validate(valid_config)
    assert not result.is_valid
    assert any("ports" in e.field for e in result.errors)


def test_empty_admin_address(valid_config):
    valid_config.admin_address = ""
    result = validate(valid_config)
    assert not result.is_valid
    assert any("admin_address" in e.field for e in result.errors)


def test_upstream_empty_name(valid_config):
    valid_config.upstreams[0].name = ""
    result = validate(valid_config)
    assert not result.is_valid
    assert any(".name" in e.field for e in result.errors)


def test_upstream_duplicate_name(valid_config):
    valid_config.upstreams[1].name = valid_config.upstreams[0].name
    result = validate(valid_config)
    assert not result.is_valid
    assert any("Duplicate" in e.message for e in result.errors)


def test_upstream_empty_host(valid_config):
    valid_config.upstreams[0].host = ""
    result = validate(valid_config)
    assert not result.is_valid
    assert any(".host" in e.field for e in result.errors)


def test_upstream_invalid_port(valid_config):
    valid_config.upstreams[0].port = -1
    result = validate(valid_config)
    assert not result.is_valid
    assert any(".port" in e.field for e in result.errors)


def test_multiple_errors_collected(valid_config):
    valid_config.listener.port = 0
    valid_config.admin_address = ""
    valid_config.upstreams[0].host = ""
    result = validate(valid_config)
    assert len(result.errors) >= 3


def test_str_invalid_lists_errors(valid_config):
    valid_config.admin_address = ""
    result = validate(valid_config)
    text = str(result)
    assert "Validation failed" in text
    assert "admin_address" in text

"""Tests for envoy_local.healthcheck module."""

import pytest
from envoy_local.healthcheck import HealthCheckConfig, default_health_check


@pytest.fixture
def valid_hc():
    return HealthCheckConfig(
        path="/health",
        interval_seconds=15,
        timeout_seconds=3,
        healthy_threshold=2,
        unhealthy_threshold=3,
    )


def test_default_health_check_is_valid():
    hc = default_health_check()
    assert hc.validate() == []


def test_valid_hc_passes_validation(valid_hc):
    assert valid_hc.validate() == []


def test_path_must_start_with_slash():
    hc = HealthCheckConfig(path="health")
    errors = hc.validate()
    assert any("path" in e for e in errors)


def test_interval_must_be_positive():
    hc = HealthCheckConfig(interval_seconds=0)
    errors = hc.validate()
    assert any("interval_seconds" in e for e in errors)


def test_timeout_must_be_positive():
    hc = HealthCheckConfig(timeout_seconds=0)
    errors = hc.validate()
    assert any("timeout_seconds" in e for e in errors)


def test_timeout_must_be_less_than_interval():
    hc = HealthCheckConfig(interval_seconds=5, timeout_seconds=5)
    errors = hc.validate()
    assert any("timeout_seconds must be less than" in e for e in errors)


def test_port_out_of_range_is_invalid():
    hc = HealthCheckConfig(interval_seconds=10, timeout_seconds=2, port=99999)
    errors = hc.validate()
    assert any("port" in e for e in errors)


def test_valid_alt_port_passes():
    hc = HealthCheckConfig(interval_seconds=10, timeout_seconds=2, port=8080)
    assert hc.validate() == []


def test_to_envoy_dict_structure(valid_hc):
    d = valid_hc.to_envoy_dict()
    assert "timeout" in d
    assert "interval" in d
    assert "http_health_check" in d
    assert d["http_health_check"]["path"] == "/health"


def test_to_envoy_dict_timeout_format(valid_hc):
    d = valid_hc.to_envoy_dict()
    assert d["timeout"] == "3s"
    assert d["interval"] == "15s"


def test_to_envoy_dict_thresholds(valid_hc):
    d = valid_hc.to_envoy_dict()
    assert d["healthy_threshold"] == 2
    assert d["unhealthy_threshold"] == 3


def test_to_envoy_dict_with_alt_port():
    hc = HealthCheckConfig(interval_seconds=10, timeout_seconds=2, port=9090)
    d = hc.to_envoy_dict()
    assert d["alt_port"] == 9090


def test_to_envoy_dict_without_alt_port(valid_hc):
    d = valid_hc.to_envoy_dict()
    assert "alt_port" not in d

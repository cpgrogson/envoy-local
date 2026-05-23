"""Tests for envoy_local.circuit_breaker module."""

import pytest
from envoy_local.circuit_breaker import (
    CircuitBreakerError,
    CircuitBreakerThresholds,
    CircuitBreakerPolicy,
    default_circuit_breaker,
)


@pytest.fixture
def valid_thresholds():
    return CircuitBreakerThresholds(
        max_connections=512,
        max_pending_requests=256,
        max_requests=1024,
        max_retries=5,
        priority="DEFAULT",
    )


def test_default_circuit_breaker_is_valid():
    cb = default_circuit_breaker()
    cb.validate()  # should not raise


def test_valid_thresholds_passes_validation(valid_thresholds):
    valid_thresholds.validate()  # should not raise


def test_zero_max_connections_is_invalid():
    t = CircuitBreakerThresholds(max_connections=0)
    with pytest.raises(CircuitBreakerError, match="max_connections"):
        t.validate()


def test_negative_max_pending_requests_is_invalid():
    t = CircuitBreakerThresholds(max_pending_requests=-1)
    with pytest.raises(CircuitBreakerError, match="max_pending_requests"):
        t.validate()


def test_zero_max_requests_is_invalid():
    t = CircuitBreakerThresholds(max_requests=0)
    with pytest.raises(CircuitBreakerError, match="max_requests"):
        t.validate()


def test_negative_max_retries_is_invalid():
    t = CircuitBreakerThresholds(max_retries=-1)
    with pytest.raises(CircuitBreakerError, match="max_retries"):
        t.validate()


def test_invalid_priority_is_rejected():
    t = CircuitBreakerThresholds(priority="LOW")
    with pytest.raises(CircuitBreakerError, match="priority"):
        t.validate()


def test_high_priority_is_valid():
    t = CircuitBreakerThresholds(priority="HIGH")
    t.validate()  # should not raise


def test_thresholds_to_envoy_dict_contains_required_keys(valid_thresholds):
    d = valid_thresholds.to_envoy_dict()
    assert "priority" in d
    assert "max_connections" in d
    assert "max_pending_requests" in d
    assert "max_requests" in d
    assert "max_retries" in d


def test_thresholds_to_envoy_dict_values(valid_thresholds):
    d = valid_thresholds.to_envoy_dict()
    assert d["max_connections"] == 512
    assert d["max_retries"] == 5
    assert d["priority"] == "DEFAULT"


def test_policy_with_no_thresholds_is_invalid():
    policy = CircuitBreakerPolicy(thresholds=[])
    with pytest.raises(CircuitBreakerError, match="threshold"):
        policy.validate()


def test_policy_to_envoy_dict_has_thresholds_list():
    policy = default_circuit_breaker()
    d = policy.to_envoy_dict()
    assert "thresholds" in d
    assert isinstance(d["thresholds"], list)
    assert len(d["thresholds"]) == 1


def test_policy_with_multiple_thresholds():
    policy = CircuitBreakerPolicy(
        thresholds=[
            CircuitBreakerThresholds(priority="DEFAULT"),
            CircuitBreakerThresholds(priority="HIGH", max_connections=256),
        ]
    )
    policy.validate()  # should not raise
    d = policy.to_envoy_dict()
    assert len(d["thresholds"]) == 2

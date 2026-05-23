"""Tests for envoy_local.retry."""
import pytest
from envoy_local.retry import RetryPolicy, default_retry_policy, RETRY_ON_OPTIONS


@pytest.fixture
def valid_policy():
    return RetryPolicy(
        num_retries=3,
        retry_on=["5xx", "connect-failure"],
        per_try_timeout_seconds=1.5,
    )


def test_default_retry_policy_is_valid():
    policy = default_retry_policy()
    assert policy.validate() == []


def test_valid_policy_passes_validation(valid_policy):
    assert valid_policy.validate() == []


def test_negative_num_retries_is_invalid():
    policy = RetryPolicy(num_retries=-1, retry_on=["5xx"])
    errors = policy.validate()
    assert any("num_retries" in e for e in errors)


def test_empty_retry_on_is_invalid():
    policy = RetryPolicy(num_retries=2, retry_on=[])
    errors = policy.validate()
    assert any("retry_on" in e for e in errors)


def test_unknown_retry_on_value_is_invalid():
    policy = RetryPolicy(num_retries=1, retry_on=["not-a-real-option"])
    errors = policy.validate()
    assert any("Unknown" in e for e in errors)


def test_zero_per_try_timeout_is_invalid():
    policy = RetryPolicy(num_retries=1, retry_on=["5xx"], per_try_timeout_seconds=0.0)
    errors = policy.validate()
    assert any("per_try_timeout_seconds" in e for e in errors)


def test_negative_per_try_timeout_is_invalid():
    policy = RetryPolicy(num_retries=1, retry_on=["5xx"], per_try_timeout_seconds=-1.0)
    errors = policy.validate()
    assert any("per_try_timeout_seconds" in e for e in errors)


def test_to_envoy_dict_contains_retry_on(valid_policy):
    d = valid_policy.to_envoy_dict()
    assert "retry_on" in d
    assert "connect-failure" in d["retry_on"]


def test_to_envoy_dict_num_retries(valid_policy):
    d = valid_policy.to_envoy_dict()
    assert d["num_retries"] == 3


def test_to_envoy_dict_per_try_timeout(valid_policy):
    d = valid_policy.to_envoy_dict()
    assert d["per_try_timeout"] == "1.5s"


def test_to_envoy_dict_no_timeout_when_none():
    policy = RetryPolicy(num_retries=1, retry_on=["5xx"])
    d = policy.to_envoy_dict()
    assert "per_try_timeout" not in d


def test_to_envoy_dict_with_host_predicate():
    policy = RetryPolicy(
        num_retries=2,
        retry_on=["5xx"],
        retry_host_predicate="envoy.retry_host_predicates.previous_hosts",
    )
    d = policy.to_envoy_dict()
    assert "retry_host_predicate" in d
    assert d["retry_host_predicate"][0]["name"] == "envoy.retry_host_predicates.previous_hosts"


def test_retry_on_options_set_is_not_empty():
    assert len(RETRY_ON_OPTIONS) > 0


def test_zero_retries_is_valid():
    policy = RetryPolicy(num_retries=0, retry_on=["5xx"])
    assert policy.validate() == []

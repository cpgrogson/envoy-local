import pytest
from envoy_local.ratelimit import (
    RateLimitDescriptor,
    RateLimitPolicy,
    default_rate_limit_policy,
)


@pytest.fixture
def valid_policy():
    return RateLimitPolicy(
        requests_per_unit=50,
        unit="SECOND",
        descriptors=[RateLimitDescriptor(key="remote_address")],
    )


def test_default_rate_limit_policy_is_valid():
    policy = default_rate_limit_policy()
    assert policy.validate() == []


def test_valid_policy_passes_validation(valid_policy):
    assert valid_policy.validate() == []


def test_zero_requests_per_unit_is_invalid():
    policy = RateLimitPolicy(requests_per_unit=0, unit="MINUTE")
    errors = policy.validate()
    assert any("requests_per_unit" in e for e in errors)


def test_negative_requests_per_unit_is_invalid():
    policy = RateLimitPolicy(requests_per_unit=-5, unit="MINUTE")
    errors = policy.validate()
    assert any("requests_per_unit" in e for e in errors)


def test_invalid_unit_is_rejected():
    policy = RateLimitPolicy(requests_per_unit=10, unit="WEEK")
    errors = policy.validate()
    assert any("unit" in e for e in errors)


def test_valid_units_are_accepted():
    for unit in ["SECOND", "MINUTE", "HOUR", "DAY"]:
        policy = RateLimitPolicy(requests_per_unit=10, unit=unit)
        assert policy.validate() == [], f"Expected {unit} to be valid"


def test_negative_stage_is_invalid():
    policy = RateLimitPolicy(requests_per_unit=10, unit="MINUTE", stage=-1)
    errors = policy.validate()
    assert any("stage" in e for e in errors)


def test_descriptor_to_envoy_dict_without_value():
    desc = RateLimitDescriptor(key="remote_address")
    result = desc.to_envoy_dict()
    assert result == {"key": "remote_address"}
    assert "value" not in result


def test_descriptor_to_envoy_dict_with_value():
    desc = RateLimitDescriptor(key="destination_cluster", value="my-service")
    result = desc.to_envoy_dict()
    assert result["key"] == "destination_cluster"
    assert result["value"] == "my-service"


def test_policy_to_envoy_dict_contains_stage(valid_policy):
    result = valid_policy.to_envoy_dict()
    assert "stage" in result
    assert result["stage"] == 0


def test_policy_to_envoy_dict_contains_actions(valid_policy):
    result = valid_policy.to_envoy_dict()
    assert "actions" in result
    assert isinstance(result["actions"], list)


def test_policy_to_envoy_dict_no_descriptors():
    policy = RateLimitPolicy(requests_per_unit=10, unit="HOUR", descriptors=[])
    result = policy.to_envoy_dict()
    assert result["actions"] == []

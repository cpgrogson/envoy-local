"""Tests for envoy_local.outlier module."""

import pytest
from envoy_local.outlier import OutlierDetectionPolicy, OutlierError, default_outlier_detection


@pytest.fixture
def valid_policy():
    return OutlierDetectionPolicy()


def test_default_outlier_detection_is_valid():
    policy = default_outlier_detection()
    policy.validate()  # should not raise


def test_valid_policy_passes_validation(valid_policy):
    valid_policy.validate()  # should not raise


def test_consecutive_5xx_zero_is_invalid():
    policy = OutlierDetectionPolicy(consecutive_5xx=0)
    with pytest.raises(OutlierError, match="consecutive_5xx"):
        policy.validate()


def test_consecutive_gateway_failure_zero_is_invalid():
    policy = OutlierDetectionPolicy(consecutive_gateway_failure=0)
    with pytest.raises(OutlierError, match="consecutive_gateway_failure"):
        policy.validate()


def test_interval_zero_is_invalid():
    policy = OutlierDetectionPolicy(interval_seconds=0)
    with pytest.raises(OutlierError, match="interval_seconds"):
        policy.validate()


def test_base_ejection_time_zero_is_invalid():
    policy = OutlierDetectionPolicy(base_ejection_time_seconds=0)
    with pytest.raises(OutlierError, match="base_ejection_time_seconds"):
        policy.validate()


def test_max_ejection_percent_above_100_is_invalid():
    policy = OutlierDetectionPolicy(max_ejection_percent=101)
    with pytest.raises(OutlierError, match="max_ejection_percent"):
        policy.validate()


def test_max_ejection_percent_zero_is_valid():
    policy = OutlierDetectionPolicy(max_ejection_percent=0)
    policy.validate()  # should not raise


def test_enforcing_consecutive_5xx_above_100_is_invalid():
    policy = OutlierDetectionPolicy(enforcing_consecutive_5xx=101)
    with pytest.raises(OutlierError, match="enforcing_consecutive_5xx"):
        policy.validate()


def test_enforcing_success_rate_above_100_is_invalid():
    policy = OutlierDetectionPolicy(enforcing_success_rate=101)
    with pytest.raises(OutlierError, match="enforcing_success_rate"):
        policy.validate()


def test_to_envoy_dict_contains_interval_as_string(valid_policy):
    d = valid_policy.to_envoy_dict()
    assert d["interval"] == "10s"


def test_to_envoy_dict_contains_base_ejection_time_as_string(valid_policy):
    d = valid_policy.to_envoy_dict()
    assert d["base_ejection_time"] == "30s"


def test_to_envoy_dict_no_local_origin_key_by_default(valid_policy):
    d = valid_policy.to_envoy_dict()
    assert "consecutive_local_origin_failure" not in d


def test_to_envoy_dict_includes_local_origin_when_set():
    policy = OutlierDetectionPolicy(consecutive_local_origin_failure=3)
    d = policy.to_envoy_dict()
    assert d["consecutive_local_origin_failure"] == 3


def test_to_envoy_dict_split_external_local_origin_errors_default(valid_policy):
    d = valid_policy.to_envoy_dict()
    assert d["split_external_local_origin_errors"] is False


def test_to_envoy_dict_raises_on_invalid_policy():
    policy = OutlierDetectionPolicy(consecutive_5xx=0)
    with pytest.raises(OutlierError):
        policy.to_envoy_dict()

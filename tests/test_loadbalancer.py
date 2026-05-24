"""Tests for envoy_local.loadbalancer."""
import pytest
from envoy_local.loadbalancer import (
    LoadBalancerPolicy,
    LoadBalancerError,
    default_load_balancer,
)


@pytest.fixture
def valid_policy():
    return LoadBalancerPolicy(policy="ROUND_ROBIN")


def test_default_load_balancer_is_valid():
    lb = default_load_balancer()
    lb.validate()  # should not raise


def test_valid_policy_passes_validation(valid_policy):
    valid_policy.validate()  # should not raise


def test_unknown_policy_raises():
    lb = LoadBalancerPolicy(policy="UNKNOWN")
    with pytest.raises(LoadBalancerError, match="Unknown lb_policy"):
        lb.validate()


def test_to_envoy_dict_contains_lb_policy(valid_policy):
    d = valid_policy.to_envoy_dict()
    assert d["lb_policy"] == "ROUND_ROBIN"


def test_ring_hash_no_extra_config_by_default():
    lb = LoadBalancerPolicy(policy="RING_HASH")
    d = lb.to_envoy_dict()
    assert "ring_hash_lb_config" not in d


def test_ring_hash_with_sizes():
    lb = LoadBalancerPolicy(policy="RING_HASH", minimum_ring_size=64, maximum_ring_size=1024)
    d = lb.to_envoy_dict()
    assert d["ring_hash_lb_config"]["minimum_ring_size"] == 64
    assert d["ring_hash_lb_config"]["maximum_ring_size"] == 1024


def test_minimum_ring_size_zero_is_invalid():
    lb = LoadBalancerPolicy(policy="RING_HASH", minimum_ring_size=0)
    with pytest.raises(LoadBalancerError, match="minimum_ring_size"):
        lb.validate()


def test_min_greater_than_max_is_invalid():
    lb = LoadBalancerPolicy(policy="RING_HASH", minimum_ring_size=512, maximum_ring_size=128)
    with pytest.raises(LoadBalancerError, match="minimum_ring_size must be <="):
        lb.validate()


def test_least_request_with_choice_count():
    lb = LoadBalancerPolicy(policy="LEAST_REQUEST", choice_count=3)
    d = lb.to_envoy_dict()
    assert d["least_request_lb_config"]["choice_count"] == 3


def test_least_request_choice_count_below_two_is_invalid():
    lb = LoadBalancerPolicy(policy="LEAST_REQUEST", choice_count=1)
    with pytest.raises(LoadBalancerError, match="choice_count must be >= 2"):
        lb.validate()


def test_maglev_policy_is_valid():
    lb = LoadBalancerPolicy(policy="MAGLEV")
    lb.validate()  # should not raise


def test_random_policy_to_dict():
    lb = LoadBalancerPolicy(policy="RANDOM")
    d = lb.to_envoy_dict()
    assert d["lb_policy"] == "RANDOM"
    assert "ring_hash_lb_config" not in d
    assert "least_request_lb_config" not in d

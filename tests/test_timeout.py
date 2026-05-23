"""Tests for envoy_local.timeout and envoy_local.cli_timeout."""
import argparse
import pytest

from envoy_local.timeout import TimeoutPolicy, default_timeout_policy
from envoy_local import cli_timeout


# ---------------------------------------------------------------------------
# TimeoutPolicy unit tests
# ---------------------------------------------------------------------------

def test_default_timeout_policy_is_valid():
    policy = default_timeout_policy()
    assert policy.validate() == []


def test_to_envoy_dict_contains_timeout():
    policy = TimeoutPolicy(route_timeout_seconds=10.0)
    d = policy.to_envoy_dict()
    assert d["timeout"] == "10.0s"


def test_to_envoy_dict_no_optional_keys_by_default():
    policy = TimeoutPolicy(route_timeout_seconds=5.0)
    d = policy.to_envoy_dict()
    assert "idle_timeout" not in d
    assert "per_try_timeout" not in d


def test_to_envoy_dict_includes_idle_timeout_when_set():
    policy = TimeoutPolicy(route_timeout_seconds=30.0, idle_timeout_seconds=60.0)
    d = policy.to_envoy_dict()
    assert d["idle_timeout"] == "60.0s"


def test_to_envoy_dict_includes_per_try_timeout_when_set():
    policy = TimeoutPolicy(route_timeout_seconds=30.0, per_try_timeout_seconds=5.0)
    d = policy.to_envoy_dict()
    assert d["per_try_timeout"] == "5.0s"


def test_negative_route_timeout_is_invalid():
    policy = TimeoutPolicy(route_timeout_seconds=-1.0)
    errors = policy.validate()
    assert any("route_timeout_seconds" in e for e in errors)


def test_zero_idle_timeout_is_invalid():
    policy = TimeoutPolicy(route_timeout_seconds=10.0, idle_timeout_seconds=0.0)
    errors = policy.validate()
    assert any("idle_timeout_seconds" in e for e in errors)


def test_per_try_timeout_exceeding_route_timeout_is_invalid():
    policy = TimeoutPolicy(route_timeout_seconds=5.0, per_try_timeout_seconds=10.0)
    errors = policy.validate()
    assert any("per_try_timeout_seconds" in e for e in errors)


def test_per_try_timeout_equal_to_route_timeout_is_valid():
    policy = TimeoutPolicy(route_timeout_seconds=10.0, per_try_timeout_seconds=10.0)
    assert policy.validate() == []


def test_zero_route_timeout_disables_check():
    # route_timeout=0 means no timeout; per_try can be anything positive
    policy = TimeoutPolicy(route_timeout_seconds=0.0, per_try_timeout_seconds=5.0)
    assert policy.validate() == []


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    cli_timeout.register(sub)
    return p


def test_register_adds_timeout_subcommand(parser):
    args = parser.parse_args(["timeout"])
    assert hasattr(args, "func")
    assert args.func is cli_timeout.cmd_timeout


def test_register_default_route_timeout(parser):
    args = parser.parse_args(["timeout"])
    assert args.route_timeout == 15.0


def test_register_custom_route_timeout(parser):
    args = parser.parse_args(["timeout", "--route-timeout", "30.0"])
    assert args.route_timeout == 30.0


def test_register_default_idle_timeout_is_none(parser):
    args = parser.parse_args(["timeout"])
    assert args.idle_timeout is None


def test_cmd_timeout_valid_prints_json(parser, capsys):
    args = parser.parse_args(["timeout", "--route-timeout", "10.0"])
    rc = cli_timeout.cmd_timeout(args)
    assert rc == 0
    captured = capsys.readouterr()
    import json
    data = json.loads(captured.out)
    assert data["timeout"] == "10.0s"


def test_cmd_timeout_invalid_returns_nonzero(parser, capsys):
    args = parser.parse_args(["timeout", "--route-timeout", "-5"])
    rc = cli_timeout.cmd_timeout(args)
    assert rc != 0

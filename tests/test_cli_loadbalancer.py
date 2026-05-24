"""Tests for envoy_local.cli_loadbalancer."""
import argparse
import pytest
from envoy_local.cli_loadbalancer import register, cmd_loadbalancer


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    register(sub)
    return p


def test_register_adds_loadbalancer_subcommand(parser):
    args = parser.parse_args(["loadbalancer"])
    assert hasattr(args, "func")


def test_register_default_policy(parser):
    args = parser.parse_args(["loadbalancer"])
    assert args.policy == "ROUND_ROBIN"


def test_register_custom_policy(parser):
    args = parser.parse_args(["loadbalancer", "--policy", "LEAST_REQUEST"])
    assert args.policy == "LEAST_REQUEST"


def test_register_default_ring_sizes_are_none(parser):
    args = parser.parse_args(["loadbalancer"])
    assert args.minimum_ring_size is None
    assert args.maximum_ring_size is None


def test_register_custom_ring_sizes(parser):
    args = parser.parse_args(
        ["loadbalancer", "--policy", "RING_HASH",
         "--minimum-ring-size", "64", "--maximum-ring-size", "512"]
    )
    assert args.minimum_ring_size == 64
    assert args.maximum_ring_size == 512


def test_cmd_loadbalancer_valid_returns_zero(capsys):
    args = argparse.Namespace(
        policy="ROUND_ROBIN",
        minimum_ring_size=None,
        maximum_ring_size=None,
        choice_count=None,
    )
    rc = cmd_loadbalancer(args)
    assert rc == 0


def test_cmd_loadbalancer_output_contains_policy(capsys):
    args = argparse.Namespace(
        policy="RANDOM",
        minimum_ring_size=None,
        maximum_ring_size=None,
        choice_count=None,
    )
    cmd_loadbalancer(args)
    out = capsys.readouterr().out
    assert "RANDOM" in out


def test_cmd_loadbalancer_invalid_returns_one(capsys):
    args = argparse.Namespace(
        policy="LEAST_REQUEST",
        minimum_ring_size=None,
        maximum_ring_size=None,
        choice_count=1,  # invalid: must be >= 2
    )
    rc = cmd_loadbalancer(args)
    assert rc == 1

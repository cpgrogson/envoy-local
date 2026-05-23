"""Tests for envoy_local.cli_healthcheck module."""

import argparse
import pytest

from envoy_local.cli_healthcheck import register, cmd_healthcheck


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    register(sub)
    return p


def test_register_adds_healthcheck_subcommand(parser):
    args = parser.parse_args(["healthcheck"])
    assert args.command == "healthcheck"


def test_register_default_path(parser):
    args = parser.parse_args(["healthcheck"])
    assert args.path == "/healthz"


def test_register_default_interval(parser):
    args = parser.parse_args(["healthcheck"])
    assert args.interval_seconds == 10


def test_register_custom_path(parser):
    args = parser.parse_args(["healthcheck", "--path", "/ping"])
    assert args.path == "/ping"


def test_register_custom_interval(parser):
    args = parser.parse_args(["healthcheck", "--interval", "30"])
    assert args.interval_seconds == 30


def test_register_validate_only_flag(parser):
    args = parser.parse_args(["healthcheck", "--validate-only"])
    assert args.validate_only is True


def test_cmd_healthcheck_valid_returns_zero(parser, capsys):
    args = parser.parse_args(["healthcheck", "--interval", "10", "--timeout", "3"])
    rc = cmd_healthcheck(args)
    assert rc == 0


def test_cmd_healthcheck_invalid_returns_one(parser, capsys):
    # timeout >= interval is invalid
    args = parser.parse_args(["healthcheck", "--interval", "5", "--timeout", "5"])
    rc = cmd_healthcheck(args)
    assert rc == 1


def test_cmd_healthcheck_output_contains_health_checks(parser, capsys):
    args = parser.parse_args(["healthcheck", "--interval", "10", "--timeout", "3"])
    cmd_healthcheck(args)
    captured = capsys.readouterr()
    assert "health_checks" in captured.out


def test_cmd_healthcheck_validate_only_no_json(parser, capsys):
    args = parser.parse_args([
        "healthcheck", "--interval", "10", "--timeout", "3", "--validate-only"
    ])
    cmd_healthcheck(args)
    captured = capsys.readouterr()
    assert "valid" in captured.out
    assert "health_checks" not in captured.out


def test_cmd_healthcheck_with_alt_port(parser, capsys):
    args = parser.parse_args([
        "healthcheck", "--interval", "10", "--timeout", "3", "--port", "8080"
    ])
    rc = cmd_healthcheck(args)
    assert rc == 0
    captured = capsys.readouterr()
    assert "8080" in captured.out

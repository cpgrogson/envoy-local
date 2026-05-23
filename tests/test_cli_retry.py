"""Tests for envoy_local.cli_retry."""
import argparse
import pytest
from envoy_local.cli_retry import register, cmd_retry


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    register(sub)
    return p


def test_register_adds_retry_subcommand(parser):
    args = parser.parse_args(["retry"])
    assert hasattr(args, "func")
    assert args.func is cmd_retry


def test_register_default_num_retries(parser):
    args = parser.parse_args(["retry"])
    assert args.num_retries == 2


def test_register_default_retry_on(parser):
    args = parser.parse_args(["retry"])
    assert "5xx" in args.retry_on


def test_register_custom_num_retries(parser):
    args = parser.parse_args(["retry", "--num-retries", "5"])
    assert args.num_retries == 5


def test_register_custom_retry_on(parser):
    args = parser.parse_args(["retry", "--retry-on", "reset", "connect-failure"])
    assert args.retry_on == ["reset", "connect-failure"]


def test_register_per_try_timeout(parser):
    args = parser.parse_args(["retry", "--per-try-timeout", "3.0"])
    assert args.per_try_timeout == 3.0


def test_cmd_retry_valid_returns_zero(parser, capsys):
    args = parser.parse_args(["retry", "--num-retries", "2", "--retry-on", "5xx"])
    rc = cmd_retry(args)
    assert rc == 0


def test_cmd_retry_output_is_valid_json(parser, capsys):
    import json
    args = parser.parse_args(["retry", "--num-retries", "1", "--retry-on", "5xx"])
    cmd_retry(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "retry_on" in data
    assert data["num_retries"] == 1


def test_cmd_retry_invalid_returns_nonzero(parser, capsys):
    args = parser.parse_args(["retry", "--num-retries", "-1", "--retry-on", "5xx"])
    rc = cmd_retry(args)
    assert rc != 0


def test_cmd_retry_default_flag(parser, capsys):
    import json
    args = parser.parse_args(["retry", "--default"])
    rc = cmd_retry(args)
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "num_retries" in data


def test_cmd_retry_unknown_retry_on_returns_nonzero(parser, capsys):
    args = parser.parse_args(["retry", "--retry-on", "not-valid"])
    rc = cmd_retry(args)
    assert rc != 0

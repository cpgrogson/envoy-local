import argparse
import pytest
from envoy_local.cli_ratelimit import register, cmd_ratelimit


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    register(sub)
    return p


def test_register_adds_ratelimit_subcommand(parser):
    args = parser.parse_args(["ratelimit"])
    assert hasattr(args, "func")


def test_register_default_requests(parser):
    args = parser.parse_args(["ratelimit"])
    assert args.requests == 1000


def test_register_default_unit(parser):
    args = parser.parse_args(["ratelimit"])
    assert args.unit == "MINUTE"


def test_register_default_stage(parser):
    args = parser.parse_args(["ratelimit"])
    assert args.stage == 0


def test_register_default_descriptor_key(parser):
    args = parser.parse_args(["ratelimit"])
    assert args.descriptor_key == "remote_address"


def test_register_default_descriptor_value_is_none(parser):
    args = parser.parse_args(["ratelimit"])
    assert args.descriptor_value is None


def test_register_custom_requests(parser):
    args = parser.parse_args(["ratelimit", "--requests", "500"])
    assert args.requests == 500


def test_register_custom_unit(parser):
    args = parser.parse_args(["ratelimit", "--unit", "HOUR"])
    assert args.unit == "HOUR"


def test_register_custom_descriptor_key(parser):
    args = parser.parse_args(["ratelimit", "--descriptor-key", "destination_cluster"])
    assert args.descriptor_key == "destination_cluster"


def test_register_custom_descriptor_value(parser):
    args = parser.parse_args(["ratelimit", "--descriptor-value", "my-cluster"])
    assert args.descriptor_value == "my-cluster"


def test_cmd_ratelimit_valid_returns_zero(parser, capsys):
    args = parser.parse_args(["ratelimit", "--requests", "100", "--unit", "SECOND"])
    result = cmd_ratelimit(args)
    assert result == 0


def test_cmd_ratelimit_invalid_returns_one(parser, capsys):
    args = parser.parse_args(["ratelimit", "--requests", "0"])
    result = cmd_ratelimit(args)
    assert result == 1


def test_cmd_ratelimit_output_contains_stage(parser, capsys):
    args = parser.parse_args(["ratelimit", "--stage", "2"])
    cmd_ratelimit(args)
    captured = capsys.readouterr()
    assert "stage" in captured.out
    assert "2" in captured.out


def test_cmd_ratelimit_negative_requests_returns_one(parser, capsys):
    args = parser.parse_args(["ratelimit", "--requests", "-5"])
    result = cmd_ratelimit(args)
    assert result == 1

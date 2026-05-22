"""Tests for the envoy_local.cli module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from envoy_local.cli import build_parser, main
from envoy_local.config import EnvoyConfig, ListenerConfig, UpstreamService
from envoy_local.validator import ValidationResult, ValidationError


@pytest.fixture
def valid_config():
    return EnvoyConfig(
        listener=ListenerConfig(port=8080),
        admin_port=9901,
        admin_address="127.0.0.1",
        upstreams=[UpstreamService(name="svc", host="localhost", port=3000)],
    )


def test_parser_validate_subcommand():
    parser = build_parser()
    args = parser.parse_args(["validate", "some_file.yaml"])
    assert args.command == "validate"
    assert args.input == "some_file.yaml"


def test_parser_generate_subcommand():
    parser = build_parser()
    args = parser.parse_args(["generate", "cfg.yaml", "-o", "out/envoy.yaml"])
    assert args.command == "generate"
    assert args.output == "out/envoy.yaml"


def test_parser_generate_default_output():
    parser = build_parser()
    args = parser.parse_args(["generate", "cfg.yaml"])
    assert args.output is None


def test_cmd_validate_valid_config(valid_config, capsys):
    with patch("envoy_local.cli.load_config_from_file", return_value=valid_config):
        rc = main(["validate", "cfg.yaml"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "valid" in captured.out.lower()


def test_cmd_validate_invalid_config(valid_config, capsys):
    valid_config.admin_address = ""
    with patch("envoy_local.cli.load_config_from_file", return_value=valid_config):
        rc = main(["validate", "cfg.yaml"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "admin_address" in captured.out


def test_cmd_validate_load_error(capsys):
    with patch("envoy_local.cli.load_config_from_file", side_effect=FileNotFoundError("not found")):
        rc = main(["validate", "missing.yaml"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_cmd_generate_success(valid_config, capsys, tmp_path):
    out_file = str(tmp_path / "envoy.yaml")
    with patch("envoy_local.cli.load_config_from_file", return_value=valid_config), \
         patch("envoy_local.cli.write_config", return_value=out_file) as mock_write:
        rc = main(["generate", "cfg.yaml", "-o", out_file])
    assert rc == 0
    mock_write.assert_called_once()
    captured = capsys.readouterr()
    assert out_file in captured.out


def test_cmd_generate_invalid_config(valid_config, capsys):
    valid_config.listener.port = 0
    with patch("envoy_local.cli.load_config_from_file", return_value=valid_config):
        rc = main(["generate", "cfg.yaml"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "validation failed" in captured.err.lower()


def test_cmd_generate_load_error(capsys):
    with patch("envoy_local.cli.load_config_from_file", side_effect=ValueError("bad yaml")):
        rc = main(["generate", "cfg.yaml"])
    assert rc == 1

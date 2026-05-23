"""Tests for envoy_local.cli_merge."""

import argparse
import os
from unittest.mock import MagicMock, patch

import pytest

from envoy_local.config import EnvoyConfig, ListenerConfig, UpstreamService, add_upstream
from envoy_local.cli_merge import register, cmd_merge


def _make_config(port: int = 8080) -> EnvoyConfig:
    cfg = EnvoyConfig(
        listener=ListenerConfig(port=port, routes=[]),
        admin_port=9901,
        upstreams=[],
    )
    return add_upstream(cfg, UpstreamService(name="svc", host="localhost", port=5000))


@pytest.fixture
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    register(sub)
    return p


def test_register_adds_merge_subcommand(parser):
    args = parser.parse_args(["merge", "a.yaml", "b.yaml"])
    assert args.inputs == ["a.yaml", "b.yaml"]


def test_register_default_output(parser):
    args = parser.parse_args(["merge", "a.yaml"])
    assert args.output == "merged_envoy.yaml"


def test_register_custom_output(parser):
    args = parser.parse_args(["merge", "a.yaml", "-o", "out.yaml"])
    assert args.output == "out.yaml"


def test_register_no_validate_flag(parser):
    args = parser.parse_args(["merge", "a.yaml", "--no-validate"])
    assert args.no_validate is True


def test_cmd_merge_returns_0_on_success(tmp_path):
    cfg_a = _make_config(8080)
    cfg_b = _make_config(9090)
    cfg_b = add_upstream(cfg_b, UpstreamService(name="svc-b", host="localhost", port=5001))
    # Remove default svc from cfg_b to avoid duplicate
    cfg_b = EnvoyConfig(
        listener=ListenerConfig(port=9090, routes=[]),
        admin_port=9901,
        upstreams=[UpstreamService(name="svc-b", host="localhost", port=5001)],
    )
    out = str(tmp_path / "merged.yaml")
    args = argparse.Namespace(inputs=["a.yaml", "b.yaml"], output=out, no_validate=False)
    with patch("envoy_local.cli_merge.load_config_from_file", side_effect=[cfg_a, cfg_b]):
        with patch("envoy_local.cli_merge.write_config") as mock_write:
            code = cmd_merge(args)
    assert code == 0
    mock_write.assert_called_once()


def test_cmd_merge_returns_1_on_load_error():
    args = argparse.Namespace(inputs=["missing.yaml"], output="out.yaml", no_validate=True)
    with patch("envoy_local.cli_merge.load_config_from_file", side_effect=FileNotFoundError("not found")):
        code = cmd_merge(args)
    assert code == 1


def test_cmd_merge_returns_1_on_invalid_merged_config():
    from envoy_local.config import EnvoyConfig, ListenerConfig
    bad_cfg = EnvoyConfig(
        listener=ListenerConfig(port=0, routes=[]),
        admin_port=9901,
        upstreams=[],
    )
    args = argparse.Namespace(inputs=["a.yaml"], output="out.yaml", no_validate=False)
    with patch("envoy_local.cli_merge.load_config_from_file", return_value=bad_cfg):
        code = cmd_merge(args)
    assert code == 1

"""Tests for envoy_local.merger."""

import pytest

from envoy_local.config import EnvoyConfig, ListenerConfig, UpstreamService, add_upstream
from envoy_local.merger import merge_configs, MergeError, MergeResult


def _make_config(listener_port: int = 8080, admin_port: int = 9901) -> EnvoyConfig:
    return EnvoyConfig(
        listener=ListenerConfig(port=listener_port, routes=[]),
        admin_port=admin_port,
        upstreams=[],
    )


def _with_upstream(cfg: EnvoyConfig, name: str, host: str = "localhost", port: int = 5000) -> EnvoyConfig:
    return add_upstream(cfg, UpstreamService(name=name, host=host, port=port))


@pytest.fixture
def config_a() -> EnvoyConfig:
    cfg = _make_config(listener_port=8080, admin_port=9901)
    return _with_upstream(cfg, "service-a", port=5001)


@pytest.fixture
def config_b() -> EnvoyConfig:
    cfg = _make_config(listener_port=9090, admin_port=9902)
    return _with_upstream(cfg, "service-b", port=5002)


def test_merge_empty_list_raises():
    with pytest.raises(MergeError):
        merge_configs([])


def test_merge_single_config_returns_copy(config_a):
    result = merge_configs([config_a])
    assert isinstance(result, MergeResult)
    assert result.merged_count == 1
    assert len(result.config.upstreams) == 1


def test_merge_uses_first_config_listener_port(config_a, config_b):
    result = merge_configs([config_a, config_b])
    assert result.config.listener.port == 8080


def test_merge_uses_first_config_admin_port(config_a, config_b):
    result = merge_configs([config_a, config_b])
    assert result.config.admin_port == 9901


def test_merge_combines_upstreams(config_a, config_b):
    result = merge_configs([config_a, config_b])
    names = {u.name for u in result.config.upstreams}
    assert "service-a" in names
    assert "service-b" in names


def test_merge_skips_duplicate_upstream_names(config_a):
    cfg_dup = _with_upstream(_make_config(), "service-a", port=9999)
    result = merge_configs([config_a, cfg_dup])
    assert "service-a" in result.skipped_upstreams
    count = sum(1 for u in result.config.upstreams if u.name == "service-a")
    assert count == 1


def test_merge_result_merged_count(config_a, config_b):
    result = merge_configs([config_a, config_b])
    assert result.merged_count == 2


def test_merge_with_explicit_base_overrides_listener(config_a, config_b):
    base = _make_config(listener_port=7070, admin_port=9999)
    result = merge_configs([config_a, config_b], base=base)
    assert result.config.listener.port == 7070
    assert result.config.admin_port == 9999


def test_merge_result_str_no_skips(config_a, config_b):
    result = merge_configs([config_a, config_b])
    assert "Merged 2 config(s)" in str(result)
    assert "skipped" not in str(result)


def test_merge_result_str_with_skips(config_a):
    cfg_dup = _with_upstream(_make_config(), "service-a")
    result = merge_configs([config_a, cfg_dup])
    assert "skipped" in str(result)
    assert "service-a" in str(result)

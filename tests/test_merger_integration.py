"""Integration tests: merge -> validate -> render pipeline."""

import yaml

from envoy_local.config import EnvoyConfig, ListenerConfig, UpstreamService, add_upstream
from envoy_local.merger import merge_configs
from envoy_local.validator import validate
from envoy_local.renderer import render


def _cfg(listener_port: int, *upstreams: UpstreamService) -> EnvoyConfig:
    cfg = EnvoyConfig(
        listener=ListenerConfig(port=listener_port, routes=[]),
        admin_port=9901,
        upstreams=[],
    )
    for u in upstreams:
        cfg = add_upstream(cfg, u)
    return cfg


def test_merge_then_validate_passes():
    cfg_a = _cfg(8080, UpstreamService("alpha", "localhost", 5001))
    cfg_b = _cfg(9090, UpstreamService("beta", "localhost", 5002))
    result = merge_configs([cfg_a, cfg_b])
    vr = validate(result.config)
    assert vr.is_valid, vr.errors


def test_merge_then_render_produces_valid_yaml():
    cfg_a = _cfg(8080, UpstreamService("svc-one", "10.0.0.1", 8001))
    cfg_b = _cfg(8080, UpstreamService("svc-two", "10.0.0.2", 8002))
    result = merge_configs([cfg_a, cfg_b])
    rendered = render(result.config)
    parsed = yaml.safe_load(rendered)
    assert isinstance(parsed, dict)


def test_merged_yaml_contains_all_clusters():
    cfg_a = _cfg(8080, UpstreamService("alpha", "localhost", 5001))
    cfg_b = _cfg(8080, UpstreamService("beta", "localhost", 5002))
    result = merge_configs([cfg_a, cfg_b])
    rendered = render(result.config)
    assert "alpha" in rendered
    assert "beta" in rendered


def test_merge_three_configs_all_upstreams_present():
    cfgs = [
        _cfg(8080, UpstreamService("a", "h", 1)),
        _cfg(8080, UpstreamService("b", "h", 2)),
        _cfg(8080, UpstreamService("c", "h", 3)),
    ]
    result = merge_configs(cfgs)
    names = {u.name for u in result.config.upstreams}
    assert names == {"a", "b", "c"}


def test_merge_deduplication_keeps_original_upstream():
    original = UpstreamService("shared", "original-host", 5000)
    duplicate = UpstreamService("shared", "other-host", 9999)
    cfg_a = _cfg(8080, original)
    cfg_b = _cfg(8080, duplicate)
    result = merge_configs([cfg_a, cfg_b])
    shared = next(u for u in result.config.upstreams if u.name == "shared")
    assert shared.host == "original-host"
    assert shared.port == 5000

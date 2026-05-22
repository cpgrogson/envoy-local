"""Tests for the config model and YAML renderer."""

import pytest
import yaml

from envoy_local.config import EnvoyConfig, ListenerConfig, UpstreamService
from envoy_local.renderer import render


@pytest.fixture
def basic_config() -> EnvoyConfig:
    cfg = EnvoyConfig(listener=ListenerConfig(port=10000), admin_port=9901)
    cfg.add_upstream("auth-service", "auth.local", 8080)
    cfg.add_upstream("order-service", "orders.local", 8081)
    return cfg


def test_render_returns_valid_yaml(basic_config):
    output = render(basic_config)
    parsed = yaml.safe_load(output)
    assert isinstance(parsed, dict)


def test_render_contains_admin_port(basic_config):
    parsed = yaml.safe_load(render(basic_config))
    admin_port = parsed["admin"]["address"]["socket_address"]["port_value"]
    assert admin_port == 9901


def test_render_listener_port(basic_config):
    parsed = yaml.safe_load(render(basic_config))
    listener_port = parsed["static_resources"]["listeners"][0]["address"]["socket_address"]["port_value"]
    assert listener_port == 10000


def test_render_creates_clusters_for_each_upstream(basic_config):
    parsed = yaml.safe_load(render(basic_config))
    clusters = parsed["static_resources"]["clusters"]
    cluster_names = {c["name"] for c in clusters}
    assert "auth_service" in cluster_names
    assert "order_service" in cluster_names


def test_render_routes_match_upstream_names(basic_config):
    parsed = yaml.safe_load(render(basic_config))
    routes = parsed["static_resources"]["listeners"][0]["filter_chains"][0]["filters"][0]["typed_config"]["route_config"]["virtual_hosts"][0]["routes"]
    prefixes = [r["match"]["prefix"] for r in routes]
    assert "/auth-service/" in prefixes
    assert "/order-service/" in prefixes


def test_validate_raises_on_no_upstreams():
    cfg = EnvoyConfig()
    with pytest.raises(ValueError, match="At least one upstream"):
        cfg.validate()


def test_validate_raises_on_duplicate_upstream_names():
    cfg = EnvoyConfig()
    cfg.add_upstream("svc", "host1.local", 8080)
    cfg.add_upstream("svc", "host2.local", 8081)
    with pytest.raises(ValueError, match="unique"):
        cfg.validate()


def test_validate_raises_on_invalid_listener_port():
    cfg = EnvoyConfig(listener=ListenerConfig(port=99999))
    cfg.add_upstream("svc", "host.local", 8080)
    with pytest.raises(ValueError, match="listener port"):
        cfg.validate()


def test_cluster_name_normalisation():
    svc = UpstreamService(name="my-cool-Service", host="host", port=80)
    assert svc.cluster_name() == "my_cool_service"

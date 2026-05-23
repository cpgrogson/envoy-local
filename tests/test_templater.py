"""Tests for envoy_local.templater."""

import pytest

from envoy_local.templater import (
    TemplateError,
    TemplateResult,
    apply_template,
)


# ---------------------------------------------------------------------------
# sidecar template
# ---------------------------------------------------------------------------

def test_sidecar_returns_template_result():
    result = apply_template("sidecar", upstream_host="api.local", upstream_port=8080)
    assert isinstance(result, TemplateResult)
    assert result.template_name == "sidecar"


def test_sidecar_default_ports():
    result = apply_template("sidecar", upstream_host="api.local", upstream_port=8080)
    assert result.config.listener.port == 10000
    assert result.config.admin_port == 9901


def test_sidecar_custom_ports():
    result = apply_template(
        "sidecar",
        upstream_host="db.local",
        upstream_port=5432,
        listener_port=15000,
        admin_port=19901,
    )
    assert result.config.listener.port == 15000
    assert result.config.admin_port == 19901


def test_sidecar_upstream_present():
    result = apply_template("sidecar", upstream_host="cache.local", upstream_port=6379)
    assert len(result.config.upstreams) == 1
    assert result.config.upstreams[0].host == "cache.local"
    assert result.config.upstreams[0].port == 6379


def test_sidecar_upstream_name_derived_from_host():
    result = apply_template("sidecar", upstream_host="my.service.local", upstream_port=9000)
    assert result.config.upstreams[0].name == "my_service_local"


def test_sidecar_explicit_upstream_name():
    result = apply_template(
        "sidecar",
        upstream_host="my.service.local",
        upstream_port=9000,
        upstream_name="my_svc",
    )
    assert result.config.upstreams[0].name == "my_svc"


def test_sidecar_missing_host_raises():
    with pytest.raises(TemplateError, match="upstream_host"):
        apply_template("sidecar", upstream_host="", upstream_port=8080)


def test_sidecar_invalid_port_raises():
    with pytest.raises(TemplateError, match="upstream_port"):
        apply_template("sidecar", upstream_host="api.local", upstream_port=0)


# ---------------------------------------------------------------------------
# egress-gateway template
# ---------------------------------------------------------------------------

def test_egress_gateway_returns_template_result():
    upstreams = [{"name": "svc_a", "host": "a.local", "port": 8001}]
    result = apply_template("egress-gateway", upstreams=upstreams)
    assert result.template_name == "egress-gateway"


def test_egress_gateway_multiple_upstreams():
    upstreams = [
        {"name": "svc_a", "host": "a.local", "port": 8001},
        {"name": "svc_b", "host": "b.local", "port": 8002},
    ]
    result = apply_template("egress-gateway", upstreams=upstreams)
    assert len(result.config.upstreams) == 2


def test_egress_gateway_empty_upstreams_raises():
    with pytest.raises(TemplateError, match="at least one"):
        apply_template("egress-gateway", upstreams=[])


def test_egress_gateway_missing_field_raises():
    with pytest.raises(TemplateError, match="missing field"):
        apply_template("egress-gateway", upstreams=[{"name": "x", "host": "x.local"}])


# ---------------------------------------------------------------------------
# unknown template
# ---------------------------------------------------------------------------

def test_unknown_template_raises():
    with pytest.raises(TemplateError, match="Unknown template"):
        apply_template("nonexistent")


def test_template_result_str():
    result = apply_template("sidecar", upstream_host="api.local", upstream_port=8080)
    s = str(result)
    assert "sidecar" in s
    assert "10000" in s

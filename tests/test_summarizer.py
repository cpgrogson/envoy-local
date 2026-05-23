"""Tests for envoy_local.summarizer."""

import pytest

from envoy_local.config import EnvoyConfig, ListenerConfig, UpstreamService, add_upstream
from envoy_local.summarizer import ConfigSummary, SummaryLine, summarize


@pytest.fixture
def basic_config():
    cfg = EnvoyConfig(
        listener=ListenerConfig(port=8080),
        admin_port=9901,
    )
    add_upstream(cfg, UpstreamService(name="serviceA", host="10.0.0.1", port=5000))
    add_upstream(cfg, UpstreamService(name="serviceB", host="10.0.0.2", port=5001))
    return cfg


@pytest.fixture
def empty_config():
    return EnvoyConfig(
        listener=ListenerConfig(port=10000),
        admin_port=9901,
    )


def test_summary_line_str():
    line = SummaryLine(label="Listener port", value="8080")
    result = str(line)
    assert "Listener port" in result
    assert "8080" in result


def test_summarize_returns_config_summary(basic_config):
    result = summarize(basic_config)
    assert isinstance(result, ConfigSummary)


def test_summarize_listener_port(basic_config):
    result = summarize(basic_config)
    d = result.as_dict()
    assert d["Listener port"] == "8080"


def test_summarize_admin_port(basic_config):
    result = summarize(basic_config)
    d = result.as_dict()
    assert d["Admin port"] == "9901"


def test_summarize_upstream_count(basic_config):
    result = summarize(basic_config)
    d = result.as_dict()
    assert d["Upstream count"] == "2"


def test_summarize_upstream_names(basic_config):
    result = summarize(basic_config)
    d = result.as_dict()
    assert "serviceA" in d["Upstreams"]
    assert "serviceB" in d["Upstreams"]


def test_summarize_upstream_addresses(basic_config):
    result = summarize(basic_config)
    d = result.as_dict()
    assert "10.0.0.1:5000" in d["Upstream addresses"]
    assert "10.0.0.2:5001" in d["Upstream addresses"]


def test_summarize_no_upstreams(empty_config):
    result = summarize(empty_config)
    d = result.as_dict()
    assert d["Upstream count"] == "0"
    assert d["Upstreams"] == "(none)"


def test_summary_str_contains_header(basic_config):
    result = summarize(basic_config)
    text = str(result)
    assert "Envoy Config Summary" in text


def test_summary_as_dict_keys(basic_config):
    result = summarize(basic_config)
    d = result.as_dict()
    assert "Listener port" in d
    assert "Admin port" in d
    assert "Upstream count" in d

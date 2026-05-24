import pytest
from envoy_local.tracing import TracingConfig, TracingError, default_tracing_config


@pytest.fixture
def valid_config():
    return TracingConfig(
        provider="zipkin",
        collector_host="zipkin.local",
        collector_port=9411,
        collector_endpoint="/api/v2/spans",
    )


def test_default_tracing_config_is_valid():
    cfg = default_tracing_config()
    cfg.validate()  # should not raise


def test_valid_config_passes_validation(valid_config):
    valid_config.validate()  # should not raise


def test_unknown_provider_raises():
    cfg = TracingConfig(provider="unknown")
    with pytest.raises(TracingError, match="Unknown provider"):
        cfg.validate()


def test_empty_collector_host_raises():
    cfg = TracingConfig(collector_host="")
    with pytest.raises(TracingError, match="collector_host"):
        cfg.validate()


def test_collector_port_zero_is_invalid():
    cfg = TracingConfig(collector_port=0)
    with pytest.raises(TracingError, match="collector_port"):
        cfg.validate()


def test_collector_port_too_large_is_invalid():
    cfg = TracingConfig(collector_port=99999)
    with pytest.raises(TracingError, match="collector_port"):
        cfg.validate()


def test_endpoint_must_start_with_slash():
    cfg = TracingConfig(collector_endpoint="api/v2/spans")
    with pytest.raises(TracingError, match="collector_endpoint"):
        cfg.validate()


def test_negative_max_path_tag_length_is_invalid():
    cfg = TracingConfig(max_path_tag_length=0)
    with pytest.raises(TracingError, match="max_path_tag_length"):
        cfg.validate()


def test_to_envoy_dict_contains_provider(valid_config):
    result = valid_config.to_envoy_dict()
    assert "provider" in result


def test_to_envoy_dict_provider_name(valid_config):
    result = valid_config.to_envoy_dict()
    assert result["provider"]["name"] == "envoy.tracers.zipkin"


def test_to_envoy_dict_collector_cluster(valid_config):
    result = valid_config.to_envoy_dict()
    typed = result["provider"]["typed_config"]
    assert typed["collector_cluster"] == "zipkin_tracing"


def test_to_envoy_dict_trace_id_128bit(valid_config):
    result = valid_config.to_envoy_dict()
    assert result["provider"]["typed_config"]["trace_id_128bit"] is True


def test_to_envoy_dict_max_path_tag_length_absent_by_default(valid_config):
    result = valid_config.to_envoy_dict()
    assert "max_path_tag_length" not in result["provider"]["typed_config"]


def test_to_envoy_dict_max_path_tag_length_included_when_set():
    cfg = TracingConfig(max_path_tag_length=256)
    result = cfg.to_envoy_dict()
    assert result["provider"]["typed_config"]["max_path_tag_length"] == 256


def test_datadog_provider_name():
    cfg = TracingConfig(provider="datadog")
    result = cfg.to_envoy_dict()
    assert result["provider"]["name"] == "envoy.tracers.datadog"

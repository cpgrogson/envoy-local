"""Tests for envoy_local.accesslog."""
import pytest
from envoy_local.accesslog import (
    AccessLogConfig,
    AccessLogError,
    default_access_log,
)


@pytest.fixture
def valid_config():
    return AccessLogConfig(sink="stdout", format="text")


def test_default_access_log_is_valid():
    cfg = default_access_log()
    cfg.validate()  # should not raise


def test_valid_stdout_config_passes(valid_config):
    valid_config.validate()  # should not raise


def test_valid_file_config_passes():
    cfg = AccessLogConfig(sink="file", format="text", path="/var/log/envoy/access.log")
    cfg.validate()  # should not raise


def test_unsupported_format_raises():
    cfg = AccessLogConfig(format="xml")
    with pytest.raises(AccessLogError, match="Unsupported format"):
        cfg.validate()


def test_unsupported_sink_raises():
    cfg = AccessLogConfig(sink="syslog")
    with pytest.raises(AccessLogError, match="Unsupported sink"):
        cfg.validate()


def test_file_sink_without_path_raises():
    cfg = AccessLogConfig(sink="file", format="text")
    with pytest.raises(AccessLogError, match="file path must be provided"):
        cfg.validate()


def test_path_set_on_non_file_sink_raises():
    cfg = AccessLogConfig(sink="stdout", path="/some/path")
    with pytest.raises(AccessLogError, match="Path should only be set"):
        cfg.validate()


def test_to_envoy_dict_stdout_structure(valid_config):
    result = valid_config.to_envoy_dict()
    assert result["name"] == "envoy.access_loggers.file"
    assert "typed_config" in result
    assert result["typed_config"]["path"] == "/dev/stdout"


def test_to_envoy_dict_stderr_uses_dev_stderr():
    cfg = AccessLogConfig(sink="stderr", format="text")
    result = cfg.to_envoy_dict()
    assert result["typed_config"]["path"] == "/dev/stderr"


def test_to_envoy_dict_file_uses_given_path():
    cfg = AccessLogConfig(sink="file", format="text", path="/tmp/access.log")
    result = cfg.to_envoy_dict()
    assert result["typed_config"]["path"] == "/tmp/access.log"


def test_to_envoy_dict_json_format_includes_log_format():
    cfg = AccessLogConfig(sink="stdout", format="json")
    result = cfg.to_envoy_dict()
    assert "log_format" in result["typed_config"]
    assert "json_format" in result["typed_config"]["log_format"]


def test_to_envoy_dict_json_format_custom_fields():
    cfg = AccessLogConfig(sink="stdout", format="json", fields=["method", "path"])
    result = cfg.to_envoy_dict()
    json_fmt = result["typed_config"]["log_format"]["json_format"]
    assert set(json_fmt.keys()) == {"method", "path"}


def test_to_envoy_dict_text_format_has_no_log_format(valid_config):
    result = valid_config.to_envoy_dict()
    assert "log_format" not in result["typed_config"]

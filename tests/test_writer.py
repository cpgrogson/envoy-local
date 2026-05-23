"""Tests for envoy_local.writer module."""

import textwrap
from io import StringIO
from pathlib import Path

import pytest
import yaml

from envoy_local.config import EnvoyConfig, ListenerConfig, UpstreamService
from envoy_local.writer import (
    DEFAULT_OUTPUT_FILENAME,
    load_config_from_file,
    write_config,
)


@pytest.fixture()
def simple_config() -> EnvoyConfig:
    upstream = UpstreamService(name="backend", host="127.0.0.1", port=8080)
    listener = ListenerConfig(port=10000, upstreams=[upstream])
    return EnvoyConfig(admin_port=9901, listeners=[listener])


def test_write_config_creates_file(simple_config, tmp_path):
    result = write_config(simple_config, output_dir=str(tmp_path))
    assert result is not None
    assert result.exists()
    assert result.name == DEFAULT_OUTPUT_FILENAME


def test_write_config_content_is_valid_yaml(simple_config, tmp_path):
    result = write_config(simple_config, output_dir=str(tmp_path))
    content = result.read_text(encoding="utf-8")
    parsed = yaml.safe_load(content)
    assert isinstance(parsed, dict)


def test_write_config_custom_filename(simple_config, tmp_path):
    result = write_config(simple_config, output_dir=str(tmp_path), filename="custom.yaml")
    assert result.name == "custom.yaml"


def test_write_config_creates_output_dir(simple_config, tmp_path):
    nested = tmp_path / "a" / "b" / "c"
    result = write_config(simple_config, output_dir=str(nested))
    assert nested.exists()
    assert result.parent == nested


def test_write_config_stdout_returns_none(simple_config, capsys):
    result = write_config(simple_config, stdout=True)
    assert result is None
    captured = capsys.readouterr()
    parsed = yaml.safe_load(captured.out)
    assert isinstance(parsed, dict)


def test_write_config_overwrites_existing_file(simple_config, tmp_path):
    """Writing config twice to the same path should overwrite without error."""
    result_first = write_config(simple_config, output_dir=str(tmp_path))
    original_content = result_first.read_text(encoding="utf-8")

    result_second = write_config(simple_config, output_dir=str(tmp_path))
    assert result_second.exists()
    assert result_second.read_text(encoding="utf-8") == original_content


def test_load_config_from_file_returns_dict(tmp_path):
    config_file = tmp_path / "test.yaml"
    config_file.write_text("static_resources:\n  clusters: []\n", encoding="utf-8")
    data = load_config_from_file(str(config_file))
    assert isinstance(data, dict)
    assert "static_resources" in data


def test_load_config_from_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_config_from_file("/nonexistent/path/envoy.yaml")


def test_load_config_from_file_invalid_yaml(tmp_path):
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text(": : : invalid\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid YAML"):
        load_config_from_file(str(bad_file))


def test_load_config_from_file_non_mapping(tmp_path):
    list_file = tmp_path / "list.yaml"
    list_file.write_text("- item1\n- item2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Expected a YAML mapping"):
        load_config_from_file(str(list_file))

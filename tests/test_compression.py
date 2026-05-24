import pytest
from envoy_local.compression import (
    CompressionPolicy,
    CompressionError,
    default_compression_policy,
    SUPPORTED_ALGORITHMS,
)


@pytest.fixture
def valid_policy():
    return CompressionPolicy()


def test_default_compression_policy_is_valid():
    policy = default_compression_policy()
    policy.validate()  # should not raise


def test_valid_policy_passes_validation(valid_policy):
    valid_policy.validate()  # should not raise


def test_unknown_algorithm_raises():
    policy = CompressionPolicy(algorithm="lzma")
    with pytest.raises(CompressionError, match="Unsupported compression algorithm"):
        policy.validate()


def test_all_supported_algorithms_are_valid():
    for algo in SUPPORTED_ALGORITHMS:
        policy = CompressionPolicy(algorithm=algo)
        policy.validate()  # should not raise


def test_negative_content_length_threshold_raises():
    policy = CompressionPolicy(content_length_threshold=-1)
    with pytest.raises(CompressionError, match="content_length_threshold"):
        policy.validate()


def test_zero_content_length_threshold_is_valid():
    policy = CompressionPolicy(content_length_threshold=0)
    policy.validate()  # should not raise


def test_empty_content_type_raises():
    policy = CompressionPolicy(content_type=[])
    with pytest.raises(CompressionError, match="content_type"):
        policy.validate()


def test_invalid_compression_level_raises():
    policy = CompressionPolicy(compression_level="ultra")
    with pytest.raises(CompressionError, match="Invalid compression_level"):
        policy.validate()


def test_valid_compression_levels():
    for level in ("best_speed", "best_compression", "default", None):
        policy = CompressionPolicy(compression_level=level)
        policy.validate()  # should not raise


def test_to_envoy_dict_contains_algorithm(valid_policy):
    result = valid_policy.to_envoy_dict()
    assert result["compressor_library"]["name"] == "gzip"


def test_to_envoy_dict_contains_content_length(valid_policy):
    result = valid_policy.to_envoy_dict()
    assert result["content_length"] == 1024


def test_to_envoy_dict_contains_content_type(valid_policy):
    result = valid_policy.to_envoy_dict()
    assert "application/json" in result["content_type"]


def test_to_envoy_dict_no_compression_level_by_default(valid_policy):
    result = valid_policy.to_envoy_dict()
    assert "compression_level" not in result["compressor_library"]["typed_config"]


def test_to_envoy_dict_includes_compression_level_when_set():
    policy = CompressionPolicy(compression_level="best_speed")
    result = policy.to_envoy_dict()
    assert result["compressor_library"]["typed_config"]["compression_level"] == "BEST_SPEED"


def test_to_envoy_dict_raises_on_invalid_policy():
    policy = CompressionPolicy(algorithm="invalid")
    with pytest.raises(CompressionError):
        policy.to_envoy_dict()

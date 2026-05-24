import pytest
from envoy_local.cors import CORSPolicy, CORSError, default_cors_policy


@pytest.fixture
def valid_policy():
    return CORSPolicy(
        allow_origin_string_match=["https://example.com"],
        allow_methods="GET,POST",
        allow_headers="content-type",
        max_age="3600",
        allow_credentials=True,
    )


def test_default_cors_policy_is_valid():
    policy = default_cors_policy()
    policy.validate()  # should not raise


def test_valid_policy_passes_validation(valid_policy):
    valid_policy.validate()  # should not raise


def test_empty_allow_origin_raises():
    policy = CORSPolicy(allow_origin_string_match=[])
    with pytest.raises(CORSError, match="allow_origin_string_match must not be empty"):
        policy.validate()


def test_empty_allow_methods_raises():
    policy = CORSPolicy(allow_methods="")
    with pytest.raises(CORSError, match="allow_methods must not be empty"):
        policy.validate()


def test_negative_max_age_raises():
    policy = CORSPolicy(max_age="-1")
    with pytest.raises(CORSError, match="non-negative"):
        policy.validate()


def test_non_integer_max_age_raises():
    policy = CORSPolicy(max_age="forever")
    with pytest.raises(CORSError, match="valid integer string"):
        policy.validate()


def test_to_envoy_dict_structure(valid_policy):
    d = valid_policy.to_envoy_dict()
    assert "allow_origin_string_match" in d
    assert "allow_methods" in d
    assert "allow_headers" in d
    assert "max_age" in d
    assert "allow_credentials" in d


def test_to_envoy_dict_origin_format(valid_policy):
    d = valid_policy.to_envoy_dict()
    origins = d["allow_origin_string_match"]
    assert isinstance(origins, list)
    assert origins[0] == {"exact": "https://example.com"}


def test_to_envoy_dict_wildcard_origin():
    policy = default_cors_policy()
    d = policy.to_envoy_dict()
    assert d["allow_origin_string_match"] == [{"exact": "*"}]


def test_expose_headers_omitted_when_empty():
    policy = CORSPolicy(expose_headers="")
    d = policy.to_envoy_dict()
    assert "expose_headers" not in d


def test_expose_headers_included_when_set():
    policy = CORSPolicy(expose_headers="x-custom-header")
    d = policy.to_envoy_dict()
    assert d["expose_headers"] == "x-custom-header"


def test_allow_credentials_false_by_default():
    policy = default_cors_policy()
    d = policy.to_envoy_dict()
    assert d["allow_credentials"] is False


def test_multiple_origins():
    policy = CORSPolicy(allow_origin_string_match=["https://a.com", "https://b.com"])
    d = policy.to_envoy_dict()
    assert len(d["allow_origin_string_match"]) == 2

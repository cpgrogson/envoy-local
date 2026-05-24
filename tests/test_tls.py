"""Tests for envoy_local.tls module."""

import pytest
from envoy_local.tls import TLSContext, TLSError, default_tls_context


@pytest.fixture
def full_tls():
    return TLSContext(
        sni="example.com",
        ca_cert_file="/etc/ssl/ca.crt",
        cert_chain_file="/etc/ssl/client.crt",
        private_key_file="/etc/ssl/client.key",
        alpn_protocols=["h2", "http/1.1"],
        verify_subject_alt_names=["example.com"],
    )


def test_default_tls_context_is_valid():
    ctx = default_tls_context()
    ctx.validate()  # should not raise


def test_default_tls_context_with_sni():
    ctx = default_tls_context(sni="mesh.local")
    assert ctx.sni == "mesh.local"


def test_cert_without_key_raises():
    ctx = TLSContext(cert_chain_file="/etc/ssl/cert.pem")
    with pytest.raises(TLSError, match="private_key_file"):
        ctx.validate()


def test_key_without_cert_raises():
    ctx = TLSContext(private_key_file="/etc/ssl/key.pem")
    with pytest.raises(TLSError, match="cert_chain_file"):
        ctx.validate()


def test_empty_alpn_raises():
    ctx = TLSContext(alpn_protocols=[])
    with pytest.raises(TLSError, match="alpn_protocols"):
        ctx.validate()


def test_upstream_dict_contains_sni(full_tls):
    d = full_tls.to_upstream_envoy_dict()
    assert d["sni"] == "example.com"


def test_upstream_dict_contains_ca_cert(full_tls):
    d = full_tls.to_upstream_envoy_dict()
    vc = d["common_tls_context"]["validation_context"]
    assert vc["trusted_ca"]["filename"] == "/etc/ssl/ca.crt"


def test_upstream_dict_contains_san(full_tls):
    d = full_tls.to_upstream_envoy_dict()
    vc = d["common_tls_context"]["validation_context"]
    assert {"exact": "example.com"} in vc["match_subject_alt_names"]


def test_upstream_dict_contains_tls_certificate(full_tls):
    d = full_tls.to_upstream_envoy_dict()
    certs = d["common_tls_context"]["tls_certificates"]
    assert certs[0]["certificate_chain"]["filename"] == "/etc/ssl/client.crt"
    assert certs[0]["private_key"]["filename"] == "/etc/ssl/client.key"


def test_upstream_dict_contains_alpn(full_tls):
    d = full_tls.to_upstream_envoy_dict()
    assert d["common_tls_context"]["alpn_protocols"] == ["h2", "http/1.1"]


def test_downstream_dict_no_sni_key(full_tls):
    d = full_tls.to_downstream_envoy_dict()
    assert "sni" not in d


def test_downstream_dict_contains_tls_certificate(full_tls):
    d = full_tls.to_downstream_envoy_dict()
    certs = d["common_tls_context"]["tls_certificates"]
    assert len(certs) == 1


def test_minimal_upstream_dict_no_common_context():
    ctx = TLSContext(sni="simple.local")
    d = ctx.to_upstream_envoy_dict()
    assert d["sni"] == "simple.local"
    # alpn_protocols is set by default, so common_tls_context will exist
    assert "alpn_protocols" in d["common_tls_context"]


def test_no_san_key_when_empty():
    ctx = TLSContext(ca_cert_file="/etc/ssl/ca.crt")
    d = ctx.to_upstream_envoy_dict()
    vc = d["common_tls_context"]["validation_context"]
    assert "match_subject_alt_names" not in vc

"""TLS context configuration for Envoy upstream and downstream connections."""

from dataclasses import dataclass, field
from typing import Optional, List


class TLSError(Exception):
    pass


@dataclass
class TLSContext:
    """Represents a TLS context for either downstream (listener) or upstream (cluster)."""

    sni: Optional[str] = None
    ca_cert_file: Optional[str] = None
    cert_chain_file: Optional[str] = None
    private_key_file: Optional[str] = None
    alpn_protocols: List[str] = field(default_factory=lambda: ["h2", "http/1.1"])
    verify_subject_alt_names: List[str] = field(default_factory=list)

    def validate(self) -> None:
        """Raise TLSError if the configuration is invalid."""
        if self.cert_chain_file and not self.private_key_file:
            raise TLSError("cert_chain_file requires private_key_file to also be set")
        if self.private_key_file and not self.cert_chain_file:
            raise TLSError("private_key_file requires cert_chain_file to also be set")
        if not self.alpn_protocols:
            raise TLSError("alpn_protocols must not be empty")

    def to_upstream_envoy_dict(self) -> dict:
        """Render as an Envoy upstreamTlsContext dict."""
        self.validate()
        ctx: dict = {}
        common = {}
        if self.ca_cert_file:
            common["validation_context"] = {
                "trusted_ca": {"filename": self.ca_cert_file}
            }
            if self.verify_subject_alt_names:
                common["validation_context"]["match_subject_alt_names"] = [
                    {"exact": san} for san in self.verify_subject_alt_names
                ]
        if self.cert_chain_file and self.private_key_file:
            common["tls_certificates"] = [
                {
                    "certificate_chain": {"filename": self.cert_chain_file},
                    "private_key": {"filename": self.private_key_file},
                }
            ]
        if self.alpn_protocols:
            common["alpn_protocols"] = self.alpn_protocols
        if common:
            ctx["common_tls_context"] = common
        if self.sni:
            ctx["sni"] = self.sni
        return ctx

    def to_downstream_envoy_dict(self) -> dict:
        """Render as an Envoy downstreamTlsContext dict."""
        self.validate()
        ctx: dict = {}
        common = {}
        if self.ca_cert_file:
            common["validation_context"] = {
                "trusted_ca": {"filename": self.ca_cert_file}
            }
        if self.cert_chain_file and self.private_key_file:
            common["tls_certificates"] = [
                {
                    "certificate_chain": {"filename": self.cert_chain_file},
                    "private_key": {"filename": self.private_key_file},
                }
            ]
        if self.alpn_protocols:
            common["alpn_protocols"] = self.alpn_protocols
        if common:
            ctx["common_tls_context"] = common
        return ctx


def default_tls_context(sni: Optional[str] = None) -> TLSContext:
    """Return a sensible default TLS context."""
    return TLSContext(sni=sni)

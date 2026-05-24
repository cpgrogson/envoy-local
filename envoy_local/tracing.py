from dataclasses import dataclass, field
from typing import Optional


class TracingError(Exception):
    pass


@dataclass
class TracingConfig:
    provider: str = "zipkin"
    collector_host: str = "localhost"
    collector_port: int = 9411
    collector_endpoint: str = "/api/v2/spans"
    trace_id_128bit: bool = True
    shared_span_context: bool = False
    max_path_tag_length: Optional[int] = None

    def validate(self) -> None:
        valid_providers = {"zipkin", "jaeger", "datadog", "lightstep"}
        if self.provider not in valid_providers:
            raise TracingError(
                f"Unknown provider '{self.provider}'. Must be one of: {sorted(valid_providers)}"
            )
        if not self.collector_host:
            raise TracingError("collector_host must not be empty")
        if not (1 <= self.collector_port <= 65535):
            raise TracingError(
                f"collector_port must be between 1 and 65535, got {self.collector_port}"
            )
        if not self.collector_endpoint.startswith("/"):
            raise TracingError("collector_endpoint must start with '/'")
        if self.max_path_tag_length is not None and self.max_path_tag_length < 1:
            raise TracingError("max_path_tag_length must be a positive integer")

    def to_envoy_dict(self) -> dict:
        self.validate()
        provider_map = {
            "zipkin": "envoy.tracers.zipkin",
            "jaeger": "envoy.tracers.zipkin",
            "datadog": "envoy.tracers.datadog",
            "lightstep": "envoy.tracers.lightstep",
        }
        typed_config: dict = {
            "@type": "type.googleapis.com/envoy.config.trace.v3.ZipkinConfig",
            "collector_cluster": f"{self.provider}_tracing",
            "collector_endpoint": self.collector_endpoint,
            "trace_id_128bit": self.trace_id_128bit,
            "shared_span_context": self.shared_span_context,
        }
        if self.max_path_tag_length is not None:
            typed_config["max_path_tag_length"] = self.max_path_tag_length
        return {
            "provider": {
                "name": provider_map[self.provider],
                "typed_config": typed_config,
            }
        }


def default_tracing_config() -> TracingConfig:
    return TracingConfig()

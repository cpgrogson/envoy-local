from dataclasses import dataclass, field
from typing import List, Optional

SUPPORTED_ALGORITHMS = {"gzip", "brotli", "zstd"}


class CompressionError(Exception):
    pass


@dataclass
class CompressionPolicy:
    algorithm: str = "gzip"
    content_length_threshold: int = 1024
    content_type: List[str] = field(default_factory=lambda: [
        "text/plain",
        "text/html",
        "application/json",
        "application/grpc",
    ])
    compression_level: Optional[str] = None  # "best_speed", "best_compression", "default"
    enabled: bool = True

    def validate(self) -> None:
        if self.algorithm not in SUPPORTED_ALGORITHMS:
            raise CompressionError(
                f"Unsupported compression algorithm '{self.algorithm}'. "
                f"Must be one of: {sorted(SUPPORTED_ALGORITHMS)}"
            )
        if self.content_length_threshold < 0:
            raise CompressionError(
                "content_length_threshold must be non-negative."
            )
        if not self.content_type:
            raise CompressionError("content_type list must not be empty.")
        valid_levels = {None, "best_speed", "best_compression", "default"}
        if self.compression_level not in valid_levels:
            raise CompressionError(
                f"Invalid compression_level '{self.compression_level}'. "
                f"Must be one of: {sorted(str(v) for v in valid_levels if v)}"
            )

    def to_envoy_dict(self) -> dict:
        self.validate()
        compressor = {
            "content_length": self.content_length_threshold,
            "content_type": self.content_type,
            "compressor_library": {
                "name": self.algorithm,
                "typed_config": {
                    "@type": f"type.googleapis.com/envoy.extensions.compression."
                             f"{self.algorithm}.compressor.v3.{self.algorithm.capitalize()}"
                },
            },
        }
        if self.compression_level:
            compressor["compressor_library"]["typed_config"]["compression_level"] = (
                self.compression_level.upper()
            )
        return compressor


def default_compression_policy() -> CompressionPolicy:
    return CompressionPolicy()

"""Access log configuration for Envoy listeners."""
from dataclasses import dataclass, field
from typing import List, Optional

SUPPORTED_FORMATS = {"json", "text"}
SUPPORTED_SINKS = {"file", "stdout", "stderr"}


class AccessLogError(Exception):
    pass


@dataclass
class AccessLogConfig:
    sink: str = "stdout"
    format: str = "text"
    path: Optional[str] = None
    fields: List[str] = field(default_factory=list)

    def validate(self) -> None:
        if self.format not in SUPPORTED_FORMATS:
            raise AccessLogError(
                f"Unsupported format '{self.format}'. Must be one of: {sorted(SUPPORTED_FORMATS)}"
            )
        if self.sink not in SUPPORTED_SINKS:
            raise AccessLogError(
                f"Unsupported sink '{self.sink}'. Must be one of: {sorted(SUPPORTED_SINKS)}"
            )
        if self.sink == "file" and not self.path:
            raise AccessLogError("A file path must be provided when sink is 'file'.")
        if self.sink != "file" and self.path:
            raise AccessLogError("Path should only be set when sink is 'file'.")

    def to_envoy_dict(self) -> dict:
        self.validate()
        if self.sink == "file":
            typed_config = {
                "@type": "type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog",
                "path": self.path,
            }
        else:
            sink_path = "/dev/stdout" if self.sink == "stdout" else "/dev/stderr"
            typed_config = {
                "@type": "type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog",
                "path": sink_path,
            }

        if self.format == "json":
            json_fields = self.fields or [
                "start_time", "method", "path", "response_code", "duration"
            ]
            typed_config["log_format"] = {
                "json_format": {f: f"%({f})s" for f in json_fields}
            }

        return {
            "name": "envoy.access_loggers.file",
            "typed_config": typed_config,
        }


def default_access_log() -> AccessLogConfig:
    return AccessLogConfig(sink="stdout", format="text")

from dataclasses import dataclass, field
from typing import List, Optional


class CORSError(Exception):
    pass


@dataclass
class CORSPolicy:
    allow_origin_string_match: List[str] = field(default_factory=lambda: ["*"])
    allow_methods: str = "GET,POST,PUT,DELETE,OPTIONS"
    allow_headers: str = "content-type,x-grpc-web"
    expose_headers: str = ""
    max_age: str = "86400"
    allow_credentials: bool = False

    def validate(self) -> None:
        if not self.allow_origin_string_match:
            raise CORSError("allow_origin_string_match must not be empty")
        if not self.allow_methods:
            raise CORSError("allow_methods must not be empty")
        try:
            age = int(self.max_age)
            if age < 0:
                raise CORSError("max_age must be a non-negative integer string")
        except ValueError:
            raise CORSError(f"max_age must be a valid integer string, got '{self.max_age}'")

    def to_envoy_dict(self) -> dict:
        self.validate()
        policy: dict = {
            "allow_origin_string_match": [
                {"exact": origin} for origin in self.allow_origin_string_match
            ],
            "allow_methods": self.allow_methods,
            "allow_headers": self.allow_headers,
            "max_age": self.max_age,
            "allow_credentials": self.allow_credentials,
        }
        if self.expose_headers:
            policy["expose_headers"] = self.expose_headers
        return policy


def default_cors_policy() -> CORSPolicy:
    return CORSPolicy()

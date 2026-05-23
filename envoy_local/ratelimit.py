from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RateLimitDescriptor:
    key: str
    value: Optional[str] = None

    def to_envoy_dict(self) -> dict:
        entry = {"key": self.key}
        if self.value is not None:
            entry["value"] = self.value
        return entry


@dataclass
class RateLimitPolicy:
    requests_per_unit: int = 100
    unit: str = "MINUTE"  # SECOND, MINUTE, HOUR, DAY
    descriptors: List[RateLimitDescriptor] = field(default_factory=list)
    stage: int = 0

    _VALID_UNITS = {"SECOND", "MINUTE", "HOUR", "DAY"}

    def validate(self) -> List[str]:
        errors: List[str] = []
        if self.requests_per_unit <= 0:
            errors.append("requests_per_unit must be a positive integer")
        if self.unit not in self._VALID_UNITS:
            errors.append(f"unit must be one of {sorted(self._VALID_UNITS)}, got '{self.unit}'")
        if self.stage < 0:
            errors.append("stage must be a non-negative integer")
        return errors

    def to_envoy_dict(self) -> dict:
        result: dict = {
            "stage": self.stage,
            "actions": [
                {"request_headers": desc.to_envoy_dict()}
                if desc.value is None
                else {"header_value_match": desc.to_envoy_dict()}
                for desc in self.descriptors
            ],
        }
        return result


def default_rate_limit_policy() -> RateLimitPolicy:
    return RateLimitPolicy(
        requests_per_unit=1000,
        unit="MINUTE",
        descriptors=[RateLimitDescriptor(key="remote_address")],
        stage=0,
    )

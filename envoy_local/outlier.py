"""Outlier detection configuration for Envoy upstream clusters."""

from dataclasses import dataclass, field
from typing import Optional


class OutlierError(Exception):
    pass


@dataclass
class OutlierDetectionPolicy:
    consecutive_5xx: int = 5
    consecutive_gateway_failure: int = 5
    interval_seconds: int = 10
    base_ejection_time_seconds: int = 30
    max_ejection_percent: int = 10
    success_rate_minimum_hosts: int = 5
    success_rate_request_volume: int = 100
    success_rate_stdev_factor: int = 1900
    enforcing_consecutive_5xx: int = 100
    enforcing_success_rate: int = 100
    split_external_local_origin_errors: bool = False
    consecutive_local_origin_failure: Optional[int] = None

    def validate(self) -> None:
        if self.consecutive_5xx < 1:
            raise OutlierError("consecutive_5xx must be >= 1")
        if self.consecutive_gateway_failure < 1:
            raise OutlierError("consecutive_gateway_failure must be >= 1")
        if self.interval_seconds < 1:
            raise OutlierError("interval_seconds must be >= 1")
        if self.base_ejection_time_seconds < 1:
            raise OutlierError("base_ejection_time_seconds must be >= 1")
        if not (0 <= self.max_ejection_percent <= 100):
            raise OutlierError("max_ejection_percent must be between 0 and 100")
        if not (0 <= self.enforcing_consecutive_5xx <= 100):
            raise OutlierError("enforcing_consecutive_5xx must be between 0 and 100")
        if not (0 <= self.enforcing_success_rate <= 100):
            raise OutlierError("enforcing_success_rate must be between 0 and 100")
        if self.success_rate_minimum_hosts < 1:
            raise OutlierError("success_rate_minimum_hosts must be >= 1")
        if self.success_rate_request_volume < 1:
            raise OutlierError("success_rate_request_volume must be >= 1")

    def to_envoy_dict(self) -> dict:
        self.validate()
        d = {
            "consecutive_5xx": self.consecutive_5xx,
            "consecutive_gateway_failure": self.consecutive_gateway_failure,
            "interval": f"{self.interval_seconds}s",
            "base_ejection_time": f"{self.base_ejection_time_seconds}s",
            "max_ejection_percent": self.max_ejection_percent,
            "success_rate_minimum_hosts": self.success_rate_minimum_hosts,
            "success_rate_request_volume": self.success_rate_request_volume,
            "success_rate_stdev_factor": self.success_rate_stdev_factor,
            "enforcing_consecutive_5xx": self.enforcing_consecutive_5xx,
            "enforcing_success_rate": self.enforcing_success_rate,
            "split_external_local_origin_errors": self.split_external_local_origin_errors,
        }
        if self.consecutive_local_origin_failure is not None:
            d["consecutive_local_origin_failure"] = self.consecutive_local_origin_failure
        return d


def default_outlier_detection() -> OutlierDetectionPolicy:
    return OutlierDetectionPolicy()

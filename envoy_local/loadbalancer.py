"""Load balancer policy configuration for Envoy clusters."""
from dataclasses import dataclass, field
from typing import Optional

VALID_POLICIES = {"ROUND_ROBIN", "LEAST_REQUEST", "RING_HASH", "RANDOM", "MAGLEV"}


class LoadBalancerError(Exception):
    pass


@dataclass
class LoadBalancerPolicy:
    policy: str = "ROUND_ROBIN"
    # For RING_HASH / MAGLEV
    minimum_ring_size: Optional[int] = None
    maximum_ring_size: Optional[int] = None
    # For LEAST_REQUEST
    choice_count: Optional[int] = None

    def validate(self) -> None:
        if self.policy not in VALID_POLICIES:
            raise LoadBalancerError(
                f"Unknown lb_policy '{self.policy}'. "
                f"Must be one of: {sorted(VALID_POLICIES)}"
            )
        if self.minimum_ring_size is not None and self.minimum_ring_size < 1:
            raise LoadBalancerError("minimum_ring_size must be >= 1")
        if self.maximum_ring_size is not None and self.maximum_ring_size < 1:
            raise LoadBalancerError("maximum_ring_size must be >= 1")
        if (
            self.minimum_ring_size is not None
            and self.maximum_ring_size is not None
            and self.minimum_ring_size > self.maximum_ring_size
        ):
            raise LoadBalancerError(
                "minimum_ring_size must be <= maximum_ring_size"
            )
        if self.choice_count is not None and self.choice_count < 2:
            raise LoadBalancerError("choice_count must be >= 2")

    def to_envoy_dict(self) -> dict:
        self.validate()
        result: dict = {"lb_policy": self.policy}
        if self.policy in {"RING_HASH", "MAGLEV"}:
            ring: dict = {}
            if self.minimum_ring_size is not None:
                ring["minimum_ring_size"] = self.minimum_ring_size
            if self.maximum_ring_size is not None:
                ring["maximum_ring_size"] = self.maximum_ring_size
            if ring:
                result["ring_hash_lb_config"] = ring
        if self.policy == "LEAST_REQUEST" and self.choice_count is not None:
            result["least_request_lb_config"] = {"choice_count": self.choice_count}
        return result


def default_load_balancer() -> LoadBalancerPolicy:
    return LoadBalancerPolicy()

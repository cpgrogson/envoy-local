"""CLI sub-command: envoy-local loadbalancer — preview a load balancer config."""
import argparse
import json
from envoy_local.loadbalancer import LoadBalancerPolicy, LoadBalancerError, VALID_POLICIES


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "loadbalancer",
        help="Preview Envoy load balancer configuration fragment",
    )
    p.add_argument(
        "--policy",
        default="ROUND_ROBIN",
        choices=sorted(VALID_POLICIES),
        help="Load balancing policy (default: ROUND_ROBIN)",
    )
    p.add_argument(
        "--minimum-ring-size",
        type=int,
        default=None,
        dest="minimum_ring_size",
        help="Minimum ring size for RING_HASH / MAGLEV",
    )
    p.add_argument(
        "--maximum-ring-size",
        type=int,
        default=None,
        dest="maximum_ring_size",
        help="Maximum ring size for RING_HASH / MAGLEV",
    )
    p.add_argument(
        "--choice-count",
        type=int,
        default=None,
        dest="choice_count",
        help="Choice count for LEAST_REQUEST (must be >= 2)",
    )
    p.set_defaults(func=cmd_loadbalancer)


def cmd_loadbalancer(args: argparse.Namespace) -> int:
    lb = LoadBalancerPolicy(
        policy=args.policy,
        minimum_ring_size=args.minimum_ring_size,
        maximum_ring_size=args.maximum_ring_size,
        choice_count=args.choice_count,
    )
    try:
        d = lb.to_envoy_dict()
        print(json.dumps(d, indent=2))
        return 0
    except LoadBalancerError as exc:
        print(f"Error: {exc}")
        return 1

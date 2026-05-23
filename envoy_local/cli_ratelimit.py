import argparse
from envoy_local.ratelimit import RateLimitPolicy, RateLimitDescriptor, default_rate_limit_policy


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "ratelimit",
        help="Generate or validate a rate limit policy configuration",
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=1000,
        metavar="N",
        help="Number of requests allowed per unit (default: 1000)",
    )
    parser.add_argument(
        "--unit",
        choices=["SECOND", "MINUTE", "HOUR", "DAY"],
        default="MINUTE",
        help="Time unit for the rate limit (default: MINUTE)",
    )
    parser.add_argument(
        "--stage",
        type=int,
        default=0,
        help="Rate limit stage (default: 0)",
    )
    parser.add_argument(
        "--descriptor-key",
        dest="descriptor_key",
        default="remote_address",
        help="Descriptor key for rate limiting (default: remote_address)",
    )
    parser.add_argument(
        "--descriptor-value",
        dest="descriptor_value",
        default=None,
        help="Optional descriptor value",
    )
    parser.set_defaults(func=cmd_ratelimit)


def cmd_ratelimit(args: argparse.Namespace) -> int:
    descriptor = RateLimitDescriptor(
        key=args.descriptor_key,
        value=args.descriptor_value,
    )
    policy = RateLimitPolicy(
        requests_per_unit=args.requests,
        unit=args.unit,
        stage=args.stage,
        descriptors=[descriptor],
    )
    errors = policy.validate()
    if errors:
        for err in errors:
            print(f"[error] {err}")
        return 1

    import yaml
    print(yaml.dump(policy.to_envoy_dict(), default_flow_style=False))
    return 0

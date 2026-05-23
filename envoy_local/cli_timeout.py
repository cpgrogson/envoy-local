"""CLI subcommand for inspecting and generating timeout policy snippets."""
import argparse
import json

from envoy_local.timeout import TimeoutPolicy


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'timeout' subcommand onto *subparsers*."""
    parser = subparsers.add_parser(
        "timeout",
        help="Show Envoy timeout policy configuration",
    )
    parser.add_argument(
        "--route-timeout",
        type=float,
        default=15.0,
        dest="route_timeout",
        help="Route timeout in seconds (default: 15.0)",
    )
    parser.add_argument(
        "--idle-timeout",
        type=float,
        default=None,
        dest="idle_timeout",
        help="Idle timeout in seconds (optional)",
    )
    parser.add_argument(
        "--per-try-timeout",
        type=float,
        default=None,
        dest="per_try_timeout",
        help="Per-try timeout in seconds (optional)",
    )
    parser.set_defaults(func=cmd_timeout)


def cmd_timeout(args: argparse.Namespace) -> int:
    """Execute the timeout subcommand; returns exit code."""
    policy = TimeoutPolicy(
        route_timeout_seconds=args.route_timeout,
        idle_timeout_seconds=args.idle_timeout,
        per_try_timeout_seconds=args.per_try_timeout,
    )
    errors = policy.validate()
    if errors:
        for err in errors:
            print(f"[error] {err}")
        return 1
    print(json.dumps(policy.to_envoy_dict(), indent=2))
    return 0

"""CLI sub-command: healthcheck — generate or validate a health check snippet."""

import argparse
import json
import sys

from envoy_local.healthcheck import HealthCheckConfig


def register(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Attach the 'healthcheck' sub-command to *subparsers*."""
    p = subparsers.add_parser(
        "healthcheck",
        help="Generate or validate an Envoy health check snippet",
    )
    p.add_argument("--path", default="/healthz", help="HTTP health check path")
    p.add_argument("--interval", type=int, default=10, dest="interval_seconds",
                   help="Check interval in seconds (default: 10)")
    p.add_argument("--timeout", type=int, default=5, dest="timeout_seconds",
                   help="Check timeout in seconds (default: 5)")
    p.add_argument("--healthy-threshold", type=int, default=2,
                   dest="healthy_threshold")
    p.add_argument("--unhealthy-threshold", type=int, default=3,
                   dest="unhealthy_threshold")
    p.add_argument("--port", type=int, default=None,
                   help="Optional alternate port for health checks")
    p.add_argument("--validate-only", action="store_true",
                   help="Only validate; do not print the snippet")
    p.set_defaults(func=cmd_healthcheck)


def cmd_healthcheck(args: argparse.Namespace) -> int:
    """Execute the healthcheck sub-command."""
    hc = HealthCheckConfig(
        path=args.path,
        interval_seconds=args.interval_seconds,
        timeout_seconds=args.timeout_seconds,
        healthy_threshold=args.healthy_threshold,
        unhealthy_threshold=args.unhealthy_threshold,
        port=args.port,
    )

    errors = hc.validate()
    if errors:
        for err in errors:
            print(f"[error] {err}", file=sys.stderr)
        return 1

    if args.validate_only:
        print("Health check config is valid.")
        return 0

    snippet = {"health_checks": [hc.to_envoy_dict()]}
    print(json.dumps(snippet, indent=2))
    return 0

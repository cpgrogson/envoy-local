"""CLI subcommand: outlier — print an Envoy outlier detection config snippet."""

import argparse
import json
import yaml

from envoy_local.outlier import OutlierDetectionPolicy, OutlierError


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "outlier",
        help="Generate an Envoy outlier detection config snippet",
    )
    parser.add_argument(
        "--consecutive-5xx",
        type=int,
        default=5,
        metavar="N",
        help="Number of consecutive 5xx errors before ejection (default: 5)",
    )
    parser.add_argument(
        "--consecutive-gw-failure",
        type=int,
        default=5,
        metavar="N",
        help="Number of consecutive gateway failures before ejection (default: 5)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        metavar="SECONDS",
        help="Analysis interval in seconds (default: 10)",
    )
    parser.add_argument(
        "--base-ejection-time",
        type=int,
        default=30,
        metavar="SECONDS",
        help="Base ejection duration in seconds (default: 30)",
    )
    parser.add_argument(
        "--max-ejection-percent",
        type=int,
        default=10,
        metavar="PCT",
        help="Maximum percentage of hosts that can be ejected (default: 10)",
    )
    parser.add_argument(
        "--format",
        choices=["yaml", "json"],
        default="yaml",
        help="Output format (default: yaml)",
    )
    parser.set_defaults(func=cmd_outlier)


def cmd_outlier(args: argparse.Namespace) -> int:
    try:
        policy = OutlierDetectionPolicy(
            consecutive_5xx=args.consecutive_5xx,
            consecutive_gateway_failure=args.consecutive_gw_failure,
            interval_seconds=args.interval,
            base_ejection_time_seconds=args.base_ejection_time,
            max_ejection_percent=args.max_ejection_percent,
        )
        d = {"outlier_detection": policy.to_envoy_dict()}
        if args.format == "json":
            print(json.dumps(d, indent=2))
        else:
            print(yaml.dump(d, default_flow_style=False).rstrip())
        return 0
    except OutlierError as exc:
        print(f"Error: {exc}")
        return 1

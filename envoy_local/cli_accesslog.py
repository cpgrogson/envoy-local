"""CLI subcommand for inspecting and previewing access log configuration."""
import argparse
import json
import sys

from envoy_local.accesslog import AccessLogConfig, AccessLogError


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "accesslog",
        help="Preview Envoy access log configuration.",
    )
    parser.add_argument(
        "--sink",
        choices=["stdout", "stderr", "file"],
        default="stdout",
        help="Where to send access logs (default: stdout).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="log_format",
        help="Log format (default: text).",
    )
    parser.add_argument(
        "--path",
        default=None,
        help="File path when --sink=file.",
    )
    parser.add_argument(
        "--fields",
        nargs="*",
        default=[],
        help="JSON fields to include (only used with --format=json).",
    )
    parser.set_defaults(func=cmd_accesslog)


def cmd_accesslog(args: argparse.Namespace) -> int:
    cfg = AccessLogConfig(
        sink=args.sink,
        format=args.log_format,
        path=args.path,
        fields=args.fields or [],
    )
    try:
        envoy_dict = cfg.to_envoy_dict()
    except AccessLogError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(envoy_dict, indent=2))
    return 0

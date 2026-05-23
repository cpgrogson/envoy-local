"""CLI helpers for the 'profile' sub-command.

This module is imported by cli.py to register the `profile` sub-command,
which runs the profiler against a saved config file and prints the report.
"""

from __future__ import annotations

import argparse
import sys

from envoy_local.profiler import profile_config
from envoy_local.writer import load_config_from_file


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Attach the *profile* sub-command to *subparsers*."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "profile",
        help="Analyze a config file and print performance / correctness hints.",
    )
    parser.add_argument(
        "config_file",
        metavar="CONFIG",
        help="Path to the YAML config file produced by 'generate'.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 when any warning or critical hint is found.",
    )
    parser.set_defaults(func=cmd_profile)


def cmd_profile(args: argparse.Namespace) -> int:
    """Entry-point for the *profile* sub-command.

    Returns an exit code (0 = success, 1 = issues found in strict mode).
    """
    try:
        config = load_config_from_file(args.config_file)
    except FileNotFoundError:
        print(f"error: file not found: {args.config_file}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not load config: {exc}", file=sys.stderr)
        return 2

    report = profile_config(config)
    print(report.summary())

    if args.strict and report.has_warnings:
        return 1
    return 0

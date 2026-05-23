"""CLI sub-command: merge multiple config files into one."""

import argparse
import sys
from typing import List

from envoy_local.merger import merge_configs, MergeError
from envoy_local.writer import load_config_from_file, write_config
from envoy_local.validator import validate


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'merge' sub-command."""
    parser = subparsers.add_parser(
        "merge",
        help="Merge multiple envoy-local config files into one",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        metavar="FILE",
        help="Input config files to merge (first provides base settings)",
    )
    parser.add_argument(
        "-o", "--output",
        default="merged_envoy.yaml",
        metavar="OUTPUT",
        help="Output file path (default: merged_envoy.yaml)",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip validation of the merged config",
    )
    parser.set_defaults(func=cmd_merge)


def cmd_merge(args: argparse.Namespace) -> int:
    """Execute the merge command."""
    configs = []
    for path in args.inputs:
        try:
            cfg = load_config_from_file(path)
            configs.append(cfg)
        except Exception as exc:  # noqa: BLE001
            print(f"Error loading '{path}': {exc}", file=sys.stderr)
            return 1

    try:
        result = merge_configs(configs)
    except MergeError as exc:
        print(f"Merge failed: {exc}", file=sys.stderr)
        return 1

    if not args.no_validate:
        vr = validate(result.config)
        if not vr.is_valid:
            print("Merged config is invalid:", file=sys.stderr)
            for err in vr.errors:
                print(f"  - {err}", file=sys.stderr)
            return 1

    write_config(result.config, filename=args.output)
    print(str(result))
    print(f"Written to: {args.output}")
    return 0

"""Simple CLI entry point for envoy-local."""

import argparse
import sys

from envoy_local.validator import validate
from envoy_local.renderer import render
from envoy_local.writer import write_config, load_config_from_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envoy-local",
        description="Spin up local Envoy proxy configs for service mesh testing.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # validate sub-command
    val_parser = subparsers.add_parser("validate", help="Validate an envoy-local config file.")
    val_parser.add_argument("input", help="Path to the YAML config file to validate.")

    # generate sub-command
    gen_parser = subparsers.add_parser("generate", help="Generate an Envoy bootstrap YAML from a config file.")
    gen_parser.add_argument("input", help="Path to the YAML config file.")
    gen_parser.add_argument("-o", "--output", default=None, help="Output file path (default: envoy_output/envoy.yaml).")

    return parser


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        config = load_config_from_file(args.input)
    except Exception as exc:
        print(f"Error loading config: {exc}", file=sys.stderr)
        return 1

    result = validate(config)
    print(result)
    return 0 if result.is_valid else 1


def cmd_generate(args: argparse.Namespace) -> int:
    try:
        config = load_config_from_file(args.input)
    except Exception as exc:
        print(f"Error loading config: {exc}", file=sys.stderr)
        return 1

    result = validate(config)
    if not result.is_valid:
        print(f"Config validation failed:\n{result}", file=sys.stderr)
        return 1

    output_path = write_config(config, output_path=args.output)
    print(f"Envoy config written to: {output_path}")
    return 0


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "generate":
        return cmd_generate(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

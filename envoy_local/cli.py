"""CLI entry point for envoy-local."""

import argparse
import logging
import sys

from envoy_local.writer import load_config_from_file, write_config
from envoy_local.validator import validate_config
from envoy_local.renderer import render
from envoy_local.watcher import ConfigWatcher

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envoy-local",
        description="Spin up local Envoy proxy configs for service mesh testing.",
    )
    sub = parser.add_subparsers(dest="command")

    # validate
    val_p = sub.add_parser("validate", help="Validate a config file.")
    val_p.add_argument("config", help="Path to the YAML config file.")

    # generate
    gen_p = sub.add_parser("generate", help="Generate an Envoy config.")
    gen_p.add_argument("config", help="Path to the YAML config file.")
    gen_p.add_argument(
        "-o", "--output", default="output/envoy.yaml", help="Output file path."
    )
    gen_p.add_argument(
        "--watch",
        action="store_true",
        default=False,
        help="Watch the config file and regenerate on changes.",
    )

    return parser


def cmd_validate(args) -> int:
    try:
        cfg = load_config_from_file(args.config)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading config: {exc}", file=sys.stderr)
        return 1
    result = validate_config(cfg)
    if result.is_valid:
        print(f"Config '{args.config}' is valid.")
        return 0
    print(f"Config '{args.config}' is invalid:", file=sys.stderr)
    for err in result.errors:
        print(f"  - {err}", file=sys.stderr)
    return 1


def cmd_generate(args) -> int:
    try:
        cfg = load_config_from_file(args.config)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading config: {exc}", file=sys.stderr)
        return 1

    def _generate(source_path: str) -> None:
        try:
            source_cfg = load_config_from_file(source_path)
            rendered = render(source_cfg)
            write_config(rendered, args.output)
            print(f"Generated Envoy config -> {args.output}")
        except Exception as exc:  # noqa: BLE001
            print(f"Generation error: {exc}", file=sys.stderr)

    rendered = render(cfg)
    write_config(rendered, args.output)
    print(f"Generated Envoy config -> {args.output}")

    if args.watch:
        watcher = ConfigWatcher(args.config, on_change=_generate)
        watcher.start()

    return 0


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "validate":
        sys.exit(cmd_validate(args))
    elif args.command == "generate":
        sys.exit(cmd_generate(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

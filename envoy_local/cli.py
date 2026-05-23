"""Command-line interface for envoy-local."""

from __future__ import annotations

import argparse
import sys

from envoy_local.config import EnvoyConfig, ListenerConfig, UpstreamService
from envoy_local.exporter import ExportError, export_snapshot, SUPPORTED_FORMATS
from envoy_local.snapshot import ConfigSnapshot
from envoy_local.validator import validate_config
from envoy_local.writer import load_config_from_file, write_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envoy-local",
        description="Spin up local Envoy proxy configs for service mesh testing.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- validate ---
    val = sub.add_parser("validate", help="Validate an Envoy config file.")
    val.add_argument("config", help="Path to config YAML file.")

    # --- generate ---
    gen = sub.add_parser("generate", help="Generate an Envoy proxy config.")
    gen.add_argument("--listener-port", type=int, default=10000)
    gen.add_argument("--admin-port", type=int, default=9901)
    gen.add_argument("--upstream", action="append", default=[], metavar="NAME:HOST:PORT")
    gen.add_argument("--output", default="envoy_output/envoy.yaml")

    # --- export ---
    exp = sub.add_parser("export", help="Export a config snapshot.")
    exp.add_argument("config", help="Path to config YAML file.")
    exp.add_argument("--format", choices=SUPPORTED_FORMATS, default="yaml")
    exp.add_argument("--output", default=None, help="Optional output file path.")

    return parser


def cmd_validate(args: argparse.Namespace) -> int:
    cfg = load_config_from_file(args.config)
    result = validate_config(cfg)
    if result.is_valid:
        print(f"✓ Config '{args.config}' is valid.")
        return 0
    print(f"✗ Validation failed for '{args.config}':")
    for err in result.errors:
        print(f"  - {err}")
    return 1


def cmd_generate(args: argparse.Namespace) -> int:
    cfg = _generate(args)
    write_config(cfg, args.output)
    print(f"✓ Config written to '{args.output}'.")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    cfg = load_config_from_file(args.config)
    snap = ConfigSnapshot.from_config(cfg)
    try:
        content = export_snapshot(snap, args.format, output_path=args.output)
    except ExportError as exc:
        print(f"✗ Export failed: {exc}", file=sys.stderr)
        return 1
    if args.output:
        print(f"✓ Snapshot exported to '{args.output}' ({args.format}).")
    else:
        print(content)
    return 0


def _generate(args: argparse.Namespace) -> EnvoyConfig:
    upstreams = []
    for raw in args.upstream:
        parts = raw.split(":")
        if len(parts) != 3:
            print(f"Invalid upstream '{raw}'. Expected NAME:HOST:PORT.", file=sys.stderr)
            sys.exit(1)
        name, host, port_str = parts
        upstreams.append(UpstreamService(name=name, host=host, port=int(port_str)))
    return EnvoyConfig(
        listener=ListenerConfig(port=args.listener_port, admin_port=args.admin_port),
        upstreams=upstreams,
    )


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {"validate": cmd_validate, "generate": cmd_generate, "export": cmd_export}
    sys.exit(handlers[args.command](args))


if __name__ == "__main__":
    main()

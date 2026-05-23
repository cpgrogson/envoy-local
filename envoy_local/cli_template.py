"""CLI sub-commands for template-based config generation."""

import argparse
import sys

from envoy_local.templater import TemplateError, apply_template
from envoy_local.writer import write_config


def register(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the 'template' sub-command on *subparsers*."""
    parser = subparsers.add_parser(
        "template",
        help="Generate an Envoy config from a built-in template",
    )
    parser.add_argument(
        "template_name",
        choices=["sidecar", "egress-gateway"],
        help="Name of the template to apply",
    )
    parser.add_argument("--listener-port", type=int, default=10000)
    parser.add_argument("--admin-port", type=int, default=9901)
    parser.add_argument("--output", default="envoy.yaml", help="Output file path")

    # sidecar-specific
    parser.add_argument("--upstream-host", default="")
    parser.add_argument("--upstream-port", type=int, default=0)
    parser.add_argument("--upstream-name", default=None)

    parser.set_defaults(func=cmd_template)


def cmd_template(args: argparse.Namespace) -> int:
    """Handle the 'template' sub-command. Returns an exit code."""
    try:
        if args.template_name == "sidecar":
            result = apply_template(
                "sidecar",
                upstream_host=args.upstream_host,
                upstream_port=args.upstream_port,
                listener_port=args.listener_port,
                admin_port=args.admin_port,
                upstream_name=args.upstream_name,
            )
        elif args.template_name == "egress-gateway":
            # egress-gateway via CLI accepts a single upstream for simplicity;
            # multiple upstreams require the Python API or a config file.
            result = apply_template(
                "egress-gateway",
                upstreams=[
                    {
                        "name": args.upstream_name or args.upstream_host.replace(".", "_"),
                        "host": args.upstream_host,
                        "port": args.upstream_port,
                    }
                ],
                listener_port=args.listener_port,
                admin_port=args.admin_port,
            )
        else:
            print(f"error: unsupported template '{args.template_name}'", file=sys.stderr)
            return 1
    except TemplateError as exc:
        print(f"Template error: {exc}", file=sys.stderr)
        return 1

    write_config(result.config, output_path=args.output)
    print(f"Generated '{args.template_name}' config → {args.output}")
    return 0

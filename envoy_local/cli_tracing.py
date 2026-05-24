import argparse
from envoy_local.tracing import TracingConfig, TracingError


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "tracing",
        help="Generate an Envoy tracing configuration snippet",
    )
    parser.add_argument(
        "--provider",
        default="zipkin",
        choices=["zipkin", "jaeger", "datadog", "lightstep"],
        help="Tracing provider (default: zipkin)",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        dest="collector_host",
        help="Tracing collector host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9411,
        dest="collector_port",
        help="Tracing collector port (default: 9411)",
    )
    parser.add_argument(
        "--endpoint",
        default="/api/v2/spans",
        dest="collector_endpoint",
        help="Collector endpoint path (default: /api/v2/spans)",
    )
    parser.add_argument(
        "--max-path-tag-length",
        type=int,
        default=None,
        dest="max_path_tag_length",
        help="Maximum length of the path tag (optional)",
    )
    parser.set_defaults(func=cmd_tracing)


def cmd_tracing(args: argparse.Namespace) -> int:
    cfg = TracingConfig(
        provider=args.provider,
        collector_host=args.collector_host,
        collector_port=args.collector_port,
        collector_endpoint=args.collector_endpoint,
        max_path_tag_length=args.max_path_tag_length,
    )
    try:
        result = cfg.to_envoy_dict()
    except TracingError as exc:
        print(f"Tracing configuration error: {exc}")
        return 1

    import yaml
    print(yaml.dump(result, default_flow_style=False))
    return 0

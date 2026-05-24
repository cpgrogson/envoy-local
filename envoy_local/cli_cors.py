import argparse
from envoy_local.cors import CORSPolicy, CORSError


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "cors",
        help="Generate a CORS policy snippet for Envoy route configuration",
    )
    parser.add_argument(
        "--origins",
        nargs="+",
        default=["*"],
        metavar="ORIGIN",
        help="Allowed origins (default: *)",
    )
    parser.add_argument(
        "--methods",
        default="GET,POST,PUT,DELETE,OPTIONS",
        help="Allowed HTTP methods (default: GET,POST,PUT,DELETE,OPTIONS)",
    )
    parser.add_argument(
        "--headers",
        default="content-type,x-grpc-web",
        help="Allowed request headers",
    )
    parser.add_argument(
        "--expose-headers",
        default="",
        dest="expose_headers",
        help="Headers to expose to the browser",
    )
    parser.add_argument(
        "--max-age",
        default="86400",
        dest="max_age",
        help="Preflight cache duration in seconds (default: 86400)",
    )
    parser.add_argument(
        "--allow-credentials",
        action="store_true",
        default=False,
        dest="allow_credentials",
        help="Allow credentials (cookies, auth headers)",
    )
    parser.set_defaults(func=cmd_cors)


def cmd_cors(args: argparse.Namespace) -> int:
    policy = CORSPolicy(
        allow_origin_string_match=args.origins,
        allow_methods=args.methods,
        allow_headers=args.headers,
        expose_headers=args.expose_headers,
        max_age=args.max_age,
        allow_credentials=args.allow_credentials,
    )
    try:
        envoy_dict = policy.to_envoy_dict()
    except CORSError as exc:
        print(f"CORS policy error: {exc}")
        return 1

    import yaml  # type: ignore
    print(yaml.dump({"cors": envoy_dict}, default_flow_style=False))
    return 0

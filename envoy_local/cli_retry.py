"""CLI sub-command: retry — inspect or generate a retry policy snippet."""
import argparse
import json
import sys

from envoy_local.retry import RetryPolicy, RETRY_ON_OPTIONS, default_retry_policy


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "retry",
        help="Generate or validate an Envoy retry policy snippet",
    )
    parser.add_argument(
        "--num-retries",
        type=int,
        default=2,
        metavar="N",
        help="Number of retries (default: 2)",
    )
    parser.add_argument(
        "--retry-on",
        nargs="+",
        default=["5xx", "gateway-error"],
        metavar="CONDITION",
        help=f"Retry conditions. Choices: {sorted(RETRY_ON_OPTIONS)}",
    )
    parser.add_argument(
        "--per-try-timeout",
        type=float,
        default=None,
        metavar="SECONDS",
        help="Per-attempt timeout in seconds",
    )
    parser.add_argument(
        "--default",
        action="store_true",
        help="Emit the built-in default retry policy and exit",
    )
    parser.set_defaults(func=cmd_retry)


def cmd_retry(args: argparse.Namespace) -> int:
    if args.default:
        policy = default_retry_policy()
    else:
        policy = RetryPolicy(
            num_retries=args.num_retries,
            retry_on=args.retry_on,
            per_try_timeout_seconds=args.per_try_timeout,
        )

    errors = policy.validate()
    if errors:
        for err in errors:
            print(f"[error] {err}", file=sys.stderr)
        return 1

    print(json.dumps(policy.to_envoy_dict(), indent=2))
    return 0

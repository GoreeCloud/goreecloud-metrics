"""Command-line entry point for the Development GoreeCloud Metrics Agent."""

from __future__ import annotations

import argparse
from getpass import getpass
import os
from pathlib import Path
import sys
import time

from .client import ClientError, enroll, submit_telemetry
from .collectors import CollectorError, collect_snapshot
from .state import StateError, load_state, save_state
from .version import current_version

_DEFAULT_STATE = Path("~/.local/state/goreecloud/metrics-agent/state.json")
_DEFAULT_INTERVAL = 30
_MIN_INTERVAL = 10
_MAX_INTERVAL = 3600
_MAX_BACKOFF = 300


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m metrics_agent")
    parser.add_argument("--state-file", type=Path, default=_DEFAULT_STATE)
    subcommands = parser.add_subparsers(dest="command", required=True)

    enroll_parser = subcommands.add_parser("enroll", help="Enroll this agent using a one-time secret.")
    enroll_parser.add_argument("--server-url", required=True)
    enroll_parser.add_argument("--enrollment-id", required=True)
    enroll_parser.add_argument("--replace-state", action="store_true")

    subcommands.add_parser("once", help="Collect and submit one telemetry sample.")

    run_parser = subcommands.add_parser("run", help="Continuously collect and submit core telemetry.")
    run_parser.add_argument("--interval-seconds", type=int, default=_DEFAULT_INTERVAL)
    return parser


def _enrollment_secret() -> str:
    secret = os.environ.get("METRICS_ENROLLMENT_SECRET")
    if secret:
        return secret
    return getpass("One-time Metrics enrollment secret: ")


def _submit_once(state_file: Path) -> None:
    state = load_state(state_file)
    snapshot = collect_snapshot()
    submit_telemetry(state, snapshot)


def _run(state_file: Path, interval: int) -> None:
    if not _MIN_INTERVAL <= interval <= _MAX_INTERVAL:
        raise ClientError(
            f"Collection interval must be between {_MIN_INTERVAL} and {_MAX_INTERVAL} seconds."
        )

    state = load_state(state_file)
    backoff = interval
    while True:
        try:
            snapshot = collect_snapshot()
            submit_telemetry(state, snapshot)
            backoff = interval
            time.sleep(interval)
        except (ClientError, CollectorError):
            print("Metrics Agent sample failed; retrying with bounded backoff.", file=sys.stderr)
            time.sleep(backoff)
            backoff = min(max(interval, backoff * 2), _MAX_BACKOFF)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "enroll":
            state = enroll(
                args.server_url,
                args.enrollment_id,
                _enrollment_secret(),
                agent_version=current_version(),
            )
            save_state(args.state_file, state, replace=args.replace_state)
            print("Metrics Agent enrollment completed.")
            return 0
        if args.command == "once":
            _submit_once(args.state_file)
            print("Metrics Agent telemetry sample accepted.")
            return 0
        if args.command == "run":
            _run(args.state_file, args.interval_seconds)
            return 0
    except KeyboardInterrupt:
        print("Metrics Agent stopped.", file=sys.stderr)
        return 130
    except (ClientError, CollectorError, StateError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

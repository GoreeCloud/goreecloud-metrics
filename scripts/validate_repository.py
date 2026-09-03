#!/usr/bin/env python3
"""Validate the minimum GoreeCloud repository documentation and secret-file boundary."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ROOT_FILES = {
    "README.md",
    "SPECIFICATIONS.md",
    "FEATURES.md",
    "BENEFITS.md",
    "COMPETITIVE-OBJECTIVES.md",
    "BRANDING.md",
    "USER-MANUAL.md",
    "LICENSE",
    "VERSION",
}


def main() -> int:
    failures: list[str] = []
    for name in sorted(REQUIRED_ROOT_FILES):
        path = ROOT / name
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            failures.append(f"missing or empty required root file: {name}")

    forbidden = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob(".env*")
        if path.name not in {".env.example", ".env.template"}
    ]
    if forbidden:
        failures.append("forbidden environment files present: " + ", ".join(forbidden))

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Repository structure validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

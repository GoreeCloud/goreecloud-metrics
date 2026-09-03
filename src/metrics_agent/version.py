"""Agent version loading from the repository source version."""

from pathlib import Path


def current_version() -> str:
    version_file = Path(__file__).resolve().parents[2] / "VERSION"
    return version_file.read_text(encoding="utf-8").strip()

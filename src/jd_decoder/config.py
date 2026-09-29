"""Configuration helpers."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

SKILL_FILES = (
    "SKILL.md",
    "references/commands/decode.md",
    "references/cross-cutting.md",
)


def load_env() -> None:
    load_dotenv()


def resolve_model() -> str:
    return os.environ.get("DECODER_MODEL", "openai:gpt-4o")


def discover_jd_paths(input_dir: str | Path) -> list[str]:
    root = Path(input_dir).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Input directory not found: {root}")
    paths = sorted(p for p in root.glob("*.md") if p.is_file())
    if not paths:
        raise FileNotFoundError(f"No .md job description files in {root}")
    return [str(p) for p in paths]

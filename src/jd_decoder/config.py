"""Configuration helpers."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from jd_decoder.models import AppConfig

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


def validate_paths(config: AppConfig) -> AppConfig:
    state = Path(config.state_path).expanduser().resolve()
    skill = Path(config.skill_dir).expanduser().resolve()
    if not state.is_file():
        raise FileNotFoundError(f"coaching_state.md not found: {state}")
    if not skill.is_dir():
        raise FileNotFoundError(f"Skill directory not found: {skill}")
    missing = [rel for rel in SKILL_FILES if not (skill / rel).is_file()]
    if missing:
        raise FileNotFoundError(
            "Skill directory is missing required files: " + ", ".join(missing)
        )
    return config.model_copy(
        update={
            "state_path": str(state),
            "skill_dir": str(skill),
            "input_dir": str(Path(config.input_dir).expanduser().resolve()),
            "output_path": str(Path(config.output_path).expanduser().resolve()),
            "model": config.model or resolve_model(),
        }
    )

"""Temp workspace setup and sandboxed file tools."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from jd_decoder.config import SKILL_FILES


class Workspace:
    """Isolated per-JD working directory."""

    def __init__(self, root: Path, temp_dir: tempfile.TemporaryDirectory[str]):
        self.root = root
        self._temp_dir = temp_dir

    def cleanup(self) -> None:
        self._temp_dir.cleanup()


def setup_workspace(jd_path: str, state_path: str, skill_dir: str) -> Workspace:
    """Create a temp dir with coaching_state.md, job.md, and skill reference files."""
    temp_dir = tempfile.TemporaryDirectory(prefix="jd_decoder_")
    root = Path(temp_dir.name)

    shutil.copy2(state_path, root / "coaching_state.md")
    shutil.copy2(jd_path, root / "job.md")

    skill_root = root / ".skill"
    for rel in SKILL_FILES:
        src = Path(skill_dir) / rel
        dest = skill_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

    return Workspace(root=root, temp_dir=temp_dir)


class ReadFileInput(BaseModel):
    path: str = Field(
        description=(
            "Relative path within the workspace, e.g. job.md, coaching_state.md, "
            ".skill/SKILL.md, .skill/references/commands/decode.md"
        )
    )


def _resolve_safe(workspace_root: Path, path: str) -> Path:
    root = workspace_root.resolve()
    candidate = (workspace_root / path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Path escapes workspace: {path}") from exc
    return candidate


def make_read_file_tool(workspace_root: Path) -> StructuredTool:
    """Build a read_file tool restricted to the given workspace root."""

    def read_file(path: str) -> str:
        try:
            target = _resolve_safe(workspace_root, path)
        except ValueError as exc:
            return f"ERROR: {exc}"
        if not target.is_file():
            return f"ERROR: file not found: {path}"
        try:
            return target.read_text(encoding="utf-8")
        except OSError as exc:
            return f"ERROR: could not read {path}: {exc}"

    return StructuredTool.from_function(
        func=read_file,
        name="read_file",
        description=(
            "Read a Markdown or text file from the decode workspace. "
            "Use relative paths: job.md, coaching_state.md, "
            ".skill/SKILL.md, .skill/references/commands/decode.md, "
            ".skill/references/cross-cutting.md"
        ),
        args_schema=ReadFileInput,
    )


def list_workspace_files(workspace_root: Path) -> str:
    files = sorted(
        str(p.relative_to(workspace_root))
        for p in workspace_root.rglob("*")
        if p.is_file()
    )
    return "\n".join(files)

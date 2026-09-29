"""Pydantic models and LangGraph state types."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, NotRequired, Self, TypedDict

from pydantic import BaseModel, Field, model_validator


class DecodeRow(BaseModel):
    """One row in the results Markdown table."""

    company: str = Field(description="Company name from the JD or decode output")
    role: str = Field(description="Role / job title")
    fit_verdict: str = Field(
        description="Strong Fit / Investable Stretch / Long-Shot Stretch / Weak Fit / Unknown"
    )
    strongest_match: str = Field(description="Strongest competency match with brief evidence")
    biggest_gap: str = Field(description="Biggest competency gap or 'none'")
    top_competencies: str = Field(
        description="Comma-separated top competencies from the Quick Scan"
    )
    path: str = Field(description="Path to the source job description file")


class AppConfig(BaseModel):
    """Runtime configuration for a decode run."""

    input_dir: str
    state_path: str
    skill_dir: str
    output_path: str
    concurrency: int = 4
    depth: str = "quick"
    model: str = "openai:gpt-4o"
    jd_paths: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _resolve_paths(self) -> Self:
        from jd_decoder.config import SKILL_FILES, discover_jd_paths, resolve_model

        state = Path(self.state_path).expanduser().resolve()
        skill = Path(self.skill_dir).expanduser().resolve()
        input_dir = Path(self.input_dir).expanduser().resolve()
        if not state.is_file():
            raise FileNotFoundError(f"coaching_state.md not found: {state}")
        if not skill.is_dir():
            raise FileNotFoundError(f"Skill directory not found: {skill}")
        missing = [rel for rel in SKILL_FILES if not (skill / rel).is_file()]
        if missing:
            raise FileNotFoundError(
                "Skill directory is missing required files: " + ", ".join(missing)
            )
        self.state_path = str(state)
        self.skill_dir = str(skill)
        self.input_dir = str(input_dir)
        self.output_path = str(Path(self.output_path).expanduser().resolve())
        self.model = self.model or resolve_model()
        self.jd_paths = discover_jd_paths(input_dir)
        return self


class WorkerResult(BaseModel):
    """Result from processing a single JD."""

    jd_path: str
    row: DecodeRow | None = None
    error: str | None = None
    raw_reply: str | None = None


def merge_results(left: list[WorkerResult], right: list[WorkerResult]) -> list[WorkerResult]:
    return left + right


class ParentState(TypedDict):
    jd_paths: list[str]
    config: dict
    results: Annotated[list[WorkerResult], merge_results]


class WorkerState(TypedDict):
    jd_path: str
    config: dict
    workspace: NotRequired[str]
    raw_reply: NotRequired[str]
    row: NotRequired[dict]
    error: NotRequired[str]

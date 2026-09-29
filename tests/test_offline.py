"""Unit tests that do not require an LLM API key."""

from __future__ import annotations

from pathlib import Path

from jd_decoder.config import SKILL_FILES, discover_jd_paths
from jd_decoder.models import AppConfig, WorkerResult
from jd_decoder.parsing import heuristic_parse
from jd_decoder.table import format_results_table
from jd_decoder.tools import make_read_file_tool, setup_workspace

ROOT = Path(__file__).resolve().parents[1]


def test_discover_jd_paths():
    paths = discover_jd_paths(ROOT / "examples" / "job_descriptions")
    assert len(paths) == 2
    assert all(p.endswith(".md") for p in paths)


def test_app_config_resolves_paths_and_discovers_jds():
    config = AppConfig(
        input_dir=str(ROOT / "examples" / "job_descriptions"),
        state_path=str(ROOT / "examples" / "coaching_state.md"),
        skill_dir=str(ROOT / "skill"),
        output_path=str(ROOT / "results.md"),
    )
    assert Path(config.state_path).is_file()
    assert Path(config.input_dir).is_dir()
    for rel in SKILL_FILES:
        assert (Path(config.skill_dir) / rel).is_file()
    assert config.jd_paths == discover_jd_paths(ROOT / "examples" / "job_descriptions")


def test_setup_workspace_and_read_file():
    jd = ROOT / "examples" / "job_descriptions" / "northbeam_senior_swe.md"
    state = ROOT / "examples" / "coaching_state.md"
    skill = ROOT / "skill"
    ws = setup_workspace(str(jd), str(state), str(skill))
    try:
        tool = make_read_file_tool(ws.root)
        job = tool.invoke({"path": "job.md"})
        assert "Northbeam Payments" in job
        skill_md = tool.invoke({"path": ".skill/SKILL.md"})
        assert "Interview Coach" in skill_md or "interview" in skill_md.lower()
        escaped = tool.invoke({"path": "../etc/passwd"})
        assert escaped.startswith("ERROR") or "escapes" in escaped.lower() or "ERROR" in escaped
    finally:
        ws.cleanup()


def test_heuristic_parse_and_table():
    raw = """
## JD Quick Scan: Acme — Senior Engineer

## Top 5 Competencies (priority order)
| # | Competency | Confidence | Type | Source |
|---|---|---|---|---|
| 1 | Distributed systems | HIGH | Screening | Requirements |
| 2 | Mentoring | MEDIUM | Differentiating | Responsibilities |

## Fit Verdict
Strong Fit — clear overlap with storybank
- Strongest match: Distributed systems (S001)
- Biggest gap: none
"""
    row = heuristic_parse(raw, "/tmp/acme.md")
    assert row.company == "Acme"
    assert row.role == "Senior Engineer"
    assert row.fit_verdict == "Strong Fit"
    assert "Distributed systems" in row.top_competencies

    md = format_results_table(
        [WorkerResult(jd_path="/tmp/acme.md", row=row)],
        ["/tmp/acme.md"],
    )
    assert "| Acme | Senior Engineer | Strong Fit |" in md


def test_path_escape_raises_via_tool_message():
    jd = ROOT / "examples" / "job_descriptions" / "northbeam_senior_swe.md"
    ws = setup_workspace(
        str(jd),
        str(ROOT / "examples" / "coaching_state.md"),
        str(ROOT / "skill"),
    )
    try:
        from jd_decoder.tools import _resolve_safe
        import pytest

        with pytest.raises(ValueError):
            _resolve_safe(ws.root, "../secret")
    finally:
        ws.cleanup()

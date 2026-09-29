"""Parse decode agent replies into table rows."""

from __future__ import annotations

import re
from pathlib import Path

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

from jd_decoder.models import DecodeRow

FIT_PATTERN = re.compile(
    r"\b(Strong Fit|Investable Stretch|Long-Shot Stretch|Weak Fit)\b",
    re.IGNORECASE,
)
TITLE_PATTERN = re.compile(
    r"##\s*JD\s*(?:Quick\s*)?Scan:\s*(.+?)\s*[—\-–]\s*(.+)",
    re.IGNORECASE,
)


def heuristic_parse(raw_reply: str, jd_path: str) -> DecodeRow:
    """Best-effort regex extraction when structured output fails."""
    company, role = _company_role_from_title(raw_reply, jd_path)
    fit = "Unknown"
    match = FIT_PATTERN.search(raw_reply)
    if match:
        fit = _canonicalize_fit(match.group(1))

    strongest = _section_bullet(raw_reply, r"Strongest match")
    biggest = _section_bullet(raw_reply, r"Biggest gap")
    competencies = _competencies_from_table(raw_reply)

    return DecodeRow(
        company=company,
        role=role,
        fit_verdict=fit,
        strongest_match=strongest or "n/a",
        biggest_gap=biggest or "n/a",
        top_competencies=competencies or "n/a",
        path=jd_path,
    )


async def structured_parse(raw_reply: str, jd_path: str, model_name: str) -> DecodeRow:
    """Extract DecodeRow via structured LLM output, with heuristic fallback."""
    llm = init_chat_model(model_name)
    structured = llm.with_structured_output(DecodeRow)
    prompt = [
        SystemMessage(
            content=(
                "Extract a single job-decode summary row from the coach reply. "
                "Use Fit Verdict exactly as one of: Strong Fit, Investable Stretch, "
                "Long-Shot Stretch, Weak Fit, or Unknown. "
                "top_competencies should be a comma-separated list. "
                f"Set path to exactly: {jd_path}"
            )
        ),
        HumanMessage(content=raw_reply),
    ]
    try:
        result = await structured.ainvoke(prompt)
        if isinstance(result, DecodeRow):
            return result.model_copy(update={"path": jd_path})
        if isinstance(result, dict):
            result["path"] = jd_path
            return DecodeRow.model_validate(result)
    except Exception:
        pass
    return heuristic_parse(raw_reply, jd_path)


def _company_role_from_title(text: str, jd_path: str) -> tuple[str, str]:
    match = TITLE_PATTERN.search(text)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    stem = Path(jd_path).stem.replace("_", " ").replace("-", " ").strip()
    return stem or "Unknown", "Unknown"


def _canonicalize_fit(value: str) -> str:
    mapping = {
        "strong fit": "Strong Fit",
        "investable stretch": "Investable Stretch",
        "long-shot stretch": "Long-Shot Stretch",
        "weak fit": "Weak Fit",
    }
    return mapping.get(value.lower(), value)


def _section_bullet(text: str, label: str) -> str | None:
    pattern = re.compile(rf"(?im)^\s*[-*]\s*{label}\s*:\s*(.+)$")
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    return None


def _competencies_from_table(text: str) -> str | None:
    rows = re.findall(
        r"^\|\s*\d+\s*\|\s*([^|]+)\|",
        text,
        flags=re.MULTILINE,
    )
    names = [r.strip() for r in rows if r.strip() and r.strip().lower() != "competency"]
    if not names:
        return None
    return ", ".join(names[:7])

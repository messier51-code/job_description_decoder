"""Markdown results table writer."""

from __future__ import annotations

from pathlib import Path

from jd_decoder.models import WorkerResult


HEADERS = (
    "Company",
    "Role",
    "Fit Verdict",
    "Strongest Match",
    "Biggest Gap",
    "Top Competencies",
    "Path",
)


def _escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def format_results_table(results: list[WorkerResult], jd_paths: list[str]) -> str:
    by_path = {r.jd_path: r for r in results}
    lines = [
        "# Job Description Decode Results",
        "",
        "| " + " | ".join(HEADERS) + " |",
        "| " + " | ".join("---" for _ in HEADERS) + " |",
    ]

    for path in jd_paths:
        result = by_path.get(path)
        if result and result.row:
            row = result.row
            cells = [
                row.company,
                row.role,
                row.fit_verdict,
                row.strongest_match,
                row.biggest_gap,
                row.top_competencies,
                row.path,
            ]
            lines.append("| " + " | ".join(_escape_cell(c) for c in cells) + " |")
        else:
            err = result.error if result else "missing result"
            lines.append(
                "| "
                + " | ".join(
                    _escape_cell(c)
                    for c in ["?", "?", "ERROR", err or "unknown", "n/a", "n/a", path]
                )
                + " |"
            )

    errors = [r for r in results if r.error]
    if errors:
        lines.extend(["", "## Errors", ""])
        for r in errors:
            lines.append(f"- `{r.jd_path}`: {_escape_cell(r.error or 'unknown')}")

    lines.append("")
    return "\n".join(lines)


def write_results_table(
    results: list[WorkerResult],
    output_path: str,
    jd_paths: list[str],
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_results_table(results, jd_paths), encoding="utf-8")

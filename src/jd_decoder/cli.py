"""CLI entrypoint."""

from __future__ import annotations

import argparse
import asyncio
import sys

from jd_decoder.config import load_env, resolve_model
from jd_decoder.graph import run_decode
from jd_decoder.models import AppConfig
from jd_decoder.table import write_results_table


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jd-decoder",
        description="Decode job descriptions in parallel using LangGraph + interview-coach decode skill",
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Directory containing job description .md files",
    )
    parser.add_argument(
        "--state",
        required=True,
        dest="state_path",
        help="Path to shared coaching_state.md (copied per JD)",
    )
    parser.add_argument(
        "--skill-dir",
        default="./skill",
        help="Path to interview-coach skill root (default: ./skill)",
    )
    parser.add_argument(
        "--output",
        default="./results.md",
        dest="output_path",
        help="Output Markdown table path (default: ./results.md)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Max parallel JD workers (default: 4)",
    )
    parser.add_argument(
        "--depth",
        choices=["quick"],
        default="quick",
        help="Decode depth (v1: quick only)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="LangChain model id (default: DECODER_MODEL or openai:gpt-4o)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    load_env()
    args = build_parser().parse_args(argv)
    try:
        config = AppConfig(
            input_dir=args.input_dir,
            state_path=args.state_path,
            skill_dir=args.skill_dir,
            output_path=args.output_path,
            concurrency=max(1, args.concurrency),
            depth=args.depth,
            model=args.model or resolve_model(),
        )
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Decoding {len(config.jd_paths)} JD(s) with model={config.model} "
        f"concurrency={config.concurrency}"
    )
    results = asyncio.run(run_decode(config.jd_paths, config))
    write_results_table(results, config.output_path, config.jd_paths)
    errors = [r for r in results if r.error]
    print(f"Wrote {config.output_path} ({len(results) - len(errors)} ok, {len(errors)} failed)")
    return 1 if errors and not any(r.row for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())

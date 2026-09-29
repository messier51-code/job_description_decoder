# Build State — job_description_decoder

**Date:** 2026-09-29  
**Branch:** `main` (ahead of `origin/main` by 1 commit: `7d63c4e initial implementation`)  
**Working tree:** uncommitted follow-up — path checks moved into `AppConfig` initialization  
**Plan:** LangGraph Job Description Decoder (v1)

## Status: complete (v1)

All plan to-dos are done. Offline unit tests pass (`5 passed`).

| To-do | Status |
|-------|--------|
| Scaffold pyproject.toml, package layout, models, config, CLI | done |
| Temp workspace setup + sandboxed `read_file` tools | done |
| LangGraph parent + worker (decode agent, parse, cleanup) | done |
| Fan-out with `Send` + concurrency; MD results table | done |
| Example JDs, stub coaching_state, README | done |

## What was built

IDE-agnostic Python CLI that:

1. `AppConfig` resolves paths and discovers `*.md` job descriptions in `--input-dir` (`config.jd_paths`)
2. Fans out LangGraph workers (`Send`) with `--concurrency`
3. Per JD: temp dir with copies of `coaching_state.md`, `job.md`, and skill refs
4. ReAct agent runs interview-coach **`decode`** (Quick Scan) via sandboxed `read_file`
5. Structured parse → row; heuristic fallback on failure
6. Writes Markdown table: Company | Role | Fit Verdict | Strongest Match | Biggest Gap | Top Competencies | Path

LLM calls use a **provider API** (`DECODER_MODEL`, default `openai:gpt-4o`). Cursor Pro does not fund these calls.

## Layout

```
pyproject.toml
README.md
.env.example
src/jd_decoder/
  cli.py, config.py, graph.py, worker.py, models.py,
  parsing.py, table.py, tools.py, __main__.py
skill/                    # vendored decode subset + LICENSE
examples/
  coaching_state.md
  job_descriptions/*.md
  expected_output.md
tests/test_offline.py
```

## Verification

```bash
source .venv/bin/activate
pytest -q
# .....  5 passed
```

Covered offline: `AppConfig` path resolution and JD discovery, workspace + sandbox read, heuristic parse + table writer, path-escape rejection.

Path checks run in `AppConfig._resolve_paths` (not as a separate CLI step after construction):

- Resolve `input_dir`, `state_path`, `skill_dir`, and `output_path`
- Require the coaching-state file, skill directory, and required skill files
- Discover `*.md` JDs via `discover_jd_paths` and store them on `jd_paths`
- CLI catches `FileNotFoundError` from construction and exits 1

`validate_paths` was removed from `config.py`. `discover_jd_paths` remains the discovery helper.

**Not run in this build (needs API key):** full live decode of example JDs.

## How to run (live)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
export OPENAI_API_KEY=...          # or matching provider for DECODER_MODEL
python -m jd_decoder \
  --input-dir ./examples/job_descriptions \
  --state ./examples/coaching_state.md \
  --skill-dir ./skill \
  --output ./results.md \
  --concurrency 4
```

## Defaults locked in plan

- Model: `init_chat_model` / env `DECODER_MODEL` / default `openai:gpt-4o`
- Skill dir: `./skill`
- Depth: `quick` only
- Parallelism: asyncio semaphore + LangGraph `Send`

## Out of scope (still)

- Batch-triage comparative section
- Writing decode results back into shared `coaching_state.md`
- Standard / Deep decode depths
- Cursor / IDE integration

# job_description_decoder

Decode and score job descriptions against a candidate's `coaching_state.md` (profile + storybank) using the interview-coach **`decode`** skill, orchestrated with **LangGraph**.

Runs as a plain Python CLI — no IDE required. LLM calls go to a normal provider API (OpenAI, Anthropic, etc.); a Cursor Pro subscription does **not** cover these calls.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Provider key matching DECODER_MODEL (default openai:gpt-4o)
export OPENAI_API_KEY=sk-...
# optional:
# export DECODER_MODEL=anthropic:claude-sonnet-4-0
# export ANTHROPIC_API_KEY=...
```

The repo vendors the skill files needed for decode under [`skill/`](skill/) (`SKILL.md`, `references/commands/decode.md`, `references/cross-cutting.md`). Point `--skill-dir` at a full interview-coach checkout if you prefer.

## Usage

```bash
python -m jd_decoder \
  --input-dir ./examples/job_descriptions \
  --state ./examples/coaching_state.md \
  --skill-dir ./skill \
  --output ./results.md \
  --concurrency 4
```

Or after install: `jd-decoder --input-dir ...` (same flags).

### Flags

| Flag | Description |
|------|-------------|
| `--input-dir` | Directory of job description `.md` files |
| `--state` | Shared `coaching_state.md` (copied into each worker temp dir) |
| `--skill-dir` | Skill root containing required MD files (default `./skill`) |
| `--output` | Results Markdown table path (default `./results.md`) |
| `--concurrency` | Max parallel JD workers (default `4`) |
| `--depth` | `quick` only in v1 |
| `--model` | Overrides `DECODER_MODEL` |

## How it works

1. Discover `*.md` files in `--input-dir`.
2. LangGraph fans out one worker per JD (`Send` API).
3. Each worker creates a temp workspace with copies of `coaching_state.md`, the JD (`job.md`), and skill references.
4. A ReAct agent reads those files via a sandboxed `read_file` tool and runs **decode** (Quick Scan).
5. A structured parse step extracts table fields; heuristic fallback if needed.
6. Results are merged into one Markdown table:

| Company | Role | Fit Verdict | Strongest Match | Biggest Gap | Top Competencies | Path |

See [`examples/expected_output.md`](examples/expected_output.md) for a sample shape.

## Examples

- [`examples/coaching_state.md`](examples/coaching_state.md) — stub profile + storybank
- [`examples/job_descriptions/`](examples/job_descriptions/) — two sample JDs

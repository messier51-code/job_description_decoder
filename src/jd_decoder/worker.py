"""Per-JD worker: workspace setup, decode agent, parse, cleanup."""

from __future__ import annotations

import asyncio
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from jd_decoder.models import AppConfig, WorkerResult
from jd_decoder.parsing import structured_parse
from jd_decoder.tools import list_workspace_files, make_read_file_tool, setup_workspace

_DECODE_SYSTEM = """You are the interview-coach skill running in headless batch mode.

Workspace files (use read_file):
{file_list}

Protocol:
1. Read `.skill/SKILL.md` for operating rules (skip interactive session greetings).
2. Read `.skill/references/commands/decode.md` for the decode workflow and Quick Scan output schema.
3. Read `.skill/references/cross-cutting.md` for Role-Fit Assessment when assessing fit.
4. Read `coaching_state.md` for Profile, Resume Analysis, and Storybank.
5. Read `job.md` for the job description.
6. Execute `decode` at Quick Scan depth only (not Standard/Deep, not batch triage).
7. Return ONLY the Quick Scan markdown document matching the schema in decode.md.
   Do not ask the user questions. Do not write files. Do not run kickoff.
   If Profile/storybank data is thin, still produce Fit Verdict with best evidence and label gaps honestly.
"""

_DECODE_USER = """Run `decode` (Quick Scan) on job.md using coaching_state.md for fit assessment.

Produce the full Quick Scan markdown output now.
"""


async def process_jd(jd_path: str, config: AppConfig, semaphore: asyncio.Semaphore) -> WorkerResult:
    """Process a single job description end-to-end under a concurrency limit."""
    async with semaphore:
        workspace = None
        try:
            workspace = setup_workspace(jd_path, config.state_path, config.skill_dir)
            raw_reply = await _run_decode_agent(workspace.root, config.model)
            row = await structured_parse(raw_reply, jd_path, config.model)
            return WorkerResult(jd_path=jd_path, row=row, raw_reply=raw_reply)
        except Exception as exc:  # noqa: BLE001 — surface per-JD failures in the table
            return WorkerResult(jd_path=jd_path, error=str(exc))
        finally:
            if workspace is not None:
                workspace.cleanup()


async def _run_decode_agent(workspace_root: Any, model_name: str) -> str:
    llm = init_chat_model(model_name)
    tools = [make_read_file_tool(workspace_root)]
    agent = create_react_agent(llm, tools)
    file_list = list_workspace_files(workspace_root)
    result = await agent.ainvoke(
        {
            "messages": [
                SystemMessage(content=_DECODE_SYSTEM.format(file_list=file_list)),
                HumanMessage(content=_DECODE_USER),
            ]
        },
        config={"recursion_limit": 40},
    )
    messages = result.get("messages", [])
    for message in reversed(messages):
        content = getattr(message, "content", None)
        if not content or getattr(message, "type", None) == "tool":
            continue
        if getattr(message, "tool_calls", None):
            continue
        text = _message_text(content)
        if text.strip():
            return text
    raise RuntimeError("Decode agent returned no assistant text")


def _message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
            elif hasattr(block, "text"):
                parts.append(str(block.text))
        return "".join(parts)
    return str(content)


def config_from_dict(data: dict) -> AppConfig:
    return AppConfig.model_validate(data)

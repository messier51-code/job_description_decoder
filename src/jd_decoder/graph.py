"""LangGraph parent graph: fan-out decode workers, collect results."""

from __future__ import annotations

import asyncio
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from jd_decoder.models import AppConfig, ParentState, WorkerResult
from jd_decoder.worker import config_from_dict, process_jd


def _fan_out(state: ParentState) -> list[Send]:
    """Emit one Send per JD path for parallel worker execution."""
    return [
        Send("process_jd", {"jd_path": path, "config": state["config"]})
        for path in state["jd_paths"]
    ]


_run_semaphore: asyncio.Semaphore | None = None


async def _process_jd_node(state: dict[str, Any]) -> dict[str, Any]:
    """Worker node invoked via Send; concurrency enforced by module-level run semaphore."""
    if _run_semaphore is None:
        raise RuntimeError("Decode run semaphore not initialized")
    config = config_from_dict(state["config"])
    result = await process_jd(state["jd_path"], config, _run_semaphore)
    return {"results": [result]}


def build_graph() -> Any:
    graph = StateGraph(ParentState)
    graph.add_node("process_jd", _process_jd_node)
    graph.add_conditional_edges(START, _fan_out, ["process_jd"])
    graph.add_edge("process_jd", END)
    return graph.compile()


async def run_decode(jd_paths: list[str], config: AppConfig) -> list[WorkerResult]:
    """Run the parent graph and return per-JD results (order may vary; table writer reorders)."""
    global _run_semaphore
    _run_semaphore = asyncio.Semaphore(config.concurrency)
    try:
        app = build_graph()
        final_state = await app.ainvoke(
            {
                "jd_paths": jd_paths,
                "config": config.model_dump(),
                "results": [],
            }
        )
        results: list[WorkerResult] = final_state.get("results", [])
        normalized: list[WorkerResult] = []
        for item in results:
            if isinstance(item, WorkerResult):
                normalized.append(item)
            else:
                normalized.append(WorkerResult.model_validate(item))
        return normalized
    finally:
        _run_semaphore = None

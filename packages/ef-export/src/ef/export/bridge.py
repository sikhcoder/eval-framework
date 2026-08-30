"""Adapters converting foreign harness state into an eval-framework Trace."""

from __future__ import annotations

from ef.core.types import ToolCall, Trace


async def trace_from_inspect(state: object, sandbox: object) -> Trace:
    """Build a Trace from an Inspect AI solver state plus its sandbox.

    Kept shape-tolerant: Inspect's internals move faster than our release cadence, and a
    brittle adapter here would silently mis-score rather than fail loudly.
    """
    messages = getattr(state, "messages", []) or []
    trace = Trace(
        instance_id=str(getattr(getattr(state, "sample", None), "id", "unknown")),
        seed=0,
        agent="inspect",
    )
    index = 0
    for message in messages:
        for block in getattr(message, "content", []) or []:
            if getattr(block, "type", None) == "tool_use":
                args = getattr(block, "input", {}) or {}
                trace.calls.append(
                    ToolCall(index=index, tool=getattr(block, "name", "bash"),
                             arguments=args, output="")
                )
                index += 1
    trace.final_message = str(getattr(state, "output", "") or "")
    read = getattr(sandbox, "read_file", None)
    if read is not None:
        for path in ("output.json", "result.csv", "REPORT.md"):
            try:
                trace.final_files[path] = await read(path)
            except Exception:
                continue
    return trace

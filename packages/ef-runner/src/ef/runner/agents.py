"""Agent adapters.

`ClaudeAgent` drives the real model through the Claude Agent SDK. `ScriptedAgent` replays a
fixed command list and exists so verifiers can be tested without spending tokens — most
verifier bugs are findable with a scripted agent long before a model is involved.
"""

from __future__ import annotations

from collections.abc import Sequence

from ef.core.protocols import Sandbox
from ef.core.types import TaskInstance, ToolCall, Trace


class ScriptedAgent:
    """Executes a fixed list of shell commands. Deterministic, free, offline."""

    def __init__(self, commands: Sequence[str], name: str = "scripted") -> None:
        self.name = name
        self.commands = list(commands)

    async def run(self, instance: TaskInstance, sandbox: Sandbox) -> Trace:
        trace = Trace(instance_id=instance.instance_id, seed=instance.seed, agent=self.name)
        for i, command in enumerate(self.commands):
            code, output = await sandbox.exec(command)
            trace.calls.append(
                ToolCall(index=i, tool="bash", arguments={"command": command},
                         output=output, exit_code=code)
            )
        trace.final_files = await _collect(sandbox)
        return trace


class ClaudeAgent:
    """Drives a real model via the Claude Agent SDK.

    The SDK is imported lazily so the framework installs and tests without it. Tool calls
    are mirrored into the Trace because the verifier scores the trace, not the sandbox.
    """

    def __init__(self, model: str = "claude-opus-5", max_turns: int = 60) -> None:
        self.name = f"claude:{model}"
        self.model = model
        self.max_turns = max_turns

    async def run(self, instance: TaskInstance, sandbox: Sandbox) -> Trace:
        try:
            from claude_agent_sdk import (  # type: ignore[import-not-found]
                ClaudeAgentOptions,
                query,
            )
        except ImportError as exc:  # pragma: no cover - depends on optional install
            raise RuntimeError(
                "claude-agent-sdk is not installed; `uv add claude-agent-sdk` to use ClaudeAgent"
            ) from exc

        trace = Trace(instance_id=instance.instance_id, seed=instance.seed, agent=self.name)
        options = ClaudeAgentOptions(
            system_prompt=(
                "You are operating inside an isolated evaluation sandbox. "
                "Complete the task using the tools available. Do not attempt to inspect or "
                "modify the grading harness."
            ),
            allowed_tools=instance.tools_summary(),
            model=self.model,
            max_turns=self.max_turns,
        )
        index = 0
        async for message in query(prompt=instance.spec.instruction, options=options):
            for call in _extract_tool_calls(message):
                call_out = await sandbox.exec(call["command"])
                trace.calls.append(
                    ToolCall(index=index, tool=call["tool"], arguments=call,
                             output=call_out[1], exit_code=call_out[0])
                )
                index += 1
            if text := _extract_text(message):
                trace.final_message = text
        trace.final_files = await _collect(sandbox)
        return trace


def _extract_tool_calls(message: object) -> list[dict]:
    """Pull bash-shaped tool calls out of an SDK message. Shape-tolerant by design."""
    content = getattr(message, "content", None)
    if not isinstance(content, list):
        return []
    calls = []
    for block in content:
        if getattr(block, "type", None) == "tool_use":
            args = getattr(block, "input", {}) or {}
            if "command" in args:
                calls.append({"tool": getattr(block, "name", "bash"), "command": args["command"]})
    return calls


def _extract_text(message: object) -> str:
    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return "\n".join(
        getattr(b, "text", "") for b in content if getattr(b, "type", None) == "text"
    )


async def _collect(sandbox: Sandbox, limit: int = 400) -> dict[str, str]:
    """Snapshot the post-rollout filesystem for the verifier."""
    files: dict[str, str] = {}
    for path in (await sandbox.list_files())[:limit]:
        try:
            files[path] = await sandbox.read_file(path)
        except Exception:
            continue
    return files

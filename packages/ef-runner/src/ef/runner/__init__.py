"""Rollout engine and agent adapters."""

from ef.runner.agents import ClaudeAgent, ScriptedAgent
from ef.runner.engine import RolloutResult, rollout

__all__ = ["ClaudeAgent", "RolloutResult", "ScriptedAgent", "rollout"]

"""Pack discovery via entry points.

A pack is a distribution exposing `ef.packs` entry points. Domain packs therefore install
and unload independently of the core, which is what keeps the proprietary packs in a
separate private repo from the Apache-2.0 core.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib.metadata import entry_points

from ef.core.protocols import TaskGenerator, Verifier

ENTRY_POINT_GROUP = "ef.packs"


@dataclass(frozen=True)
class Pack:
    """A domain bundle: named tasks, each with a generator and a verifier."""

    name: str
    generators: dict[str, TaskGenerator] = field(default_factory=dict)
    verifiers: dict[str, Verifier] = field(default_factory=dict)

    def task_ids(self) -> list[str]:
        return sorted(self.generators)


class Registry:
    """Lazily discovers installed packs and resolves `<pack>/<task>` identifiers."""

    def __init__(self) -> None:
        self._packs: dict[str, Pack] | None = None

    def packs(self) -> dict[str, Pack]:
        if self._packs is None:
            self._packs = {}
            for ep in entry_points(group=ENTRY_POINT_GROUP):
                pack = ep.load()
                self._packs[pack.name] = pack
        return self._packs

    def register(self, pack: Pack) -> None:
        """Register a pack directly. Used by tests and by in-repo development."""
        if self._packs is None:
            self._packs = {}
        self._packs[pack.name] = pack

    def resolve(self, task_id: str) -> tuple[TaskGenerator, Verifier]:
        """Resolve `<pack>/<task>` to its generator and verifier."""
        if "/" not in task_id:
            raise ValueError(f"task id must be '<pack>/<task>', got {task_id!r}")
        pack_name, task_name = task_id.split("/", 1)
        packs = self.packs()
        if pack_name not in packs:
            known = ", ".join(sorted(packs)) or "none installed"
            raise KeyError(f"unknown pack {pack_name!r} (known: {known})")
        pack = packs[pack_name]
        if task_name not in pack.generators:
            known = ", ".join(pack.task_ids()) or "none"
            raise KeyError(f"unknown task {task_name!r} in pack {pack_name!r} (known: {known})")
        return pack.generators[task_name], pack.verifiers[task_name]

    def all_task_ids(self) -> list[str]:
        return sorted(
            f"{name}/{task}" for name, pack in self.packs().items() for task in pack.task_ids()
        )


REGISTRY = Registry()

"""Local subprocess sandbox — a temp directory, no isolation.

Intended for fast unit tests and verifier development only. It provides no security
boundary whatsoever and must never execute untrusted model output. `DockerSandbox` is the
default for anything real.
"""

from __future__ import annotations

import asyncio
import shutil
import tempfile
from pathlib import Path

from ef.core.types import TaskInstance


class LocalSandbox:
    """Runs commands in a temp directory on the host. Test-only."""

    def __init__(self) -> None:
        self._root: Path | None = None

    @property
    def root(self) -> Path:
        if self._root is None:
            raise RuntimeError("sandbox not started")
        return self._root

    async def start(self, instance: TaskInstance) -> None:
        self._root = Path(tempfile.mkdtemp(prefix="ef-local-"))
        for rel, content in instance.files.items():
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)

    async def exec(self, command: str, timeout: int = 120) -> tuple[int, str]:
        proc = await asyncio.create_subprocess_shell(
            command,
            cwd=self.root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        try:
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except TimeoutError:
            proc.kill()
            return 124, f"timeout after {timeout}s"
        return proc.returncode or 0, stdout.decode(errors="replace")

    async def read_file(self, path: str) -> str:
        return (self.root / path).read_text()

    async def write_file(self, path: str, content: str) -> None:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    async def list_files(self, path: str = ".") -> list[str]:
        base = self.root / path
        return sorted(str(p.relative_to(self.root)) for p in base.rglob("*") if p.is_file())

    async def stop(self) -> None:
        if self._root is not None:
            shutil.rmtree(self._root, ignore_errors=True)
            self._root = None

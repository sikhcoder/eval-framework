"""Docker-backed sandbox. The default for real rollouts.

Network is denied by default: an agent that can reach the internet can exfiltrate a task,
fetch a solution, or contaminate a future benchmark. Packs must opt in explicitly.
"""

from __future__ import annotations

import asyncio
import shlex
import tarfile
import tempfile
from io import BytesIO
from pathlib import Path

from ef.core.types import TaskInstance


class DockerSandbox:
    """Wraps a container for the lifetime of one rollout."""

    def __init__(self) -> None:
        self._container = None
        self._workdir = "/workspace"

    async def start(self, instance: TaskInstance) -> None:
        import docker  # imported lazily so ef-core stays importable without a daemon

        spec = instance.spec.sandbox
        self._workdir = spec.workdir
        client = docker.from_env()
        image = spec.image or "python:3.12-slim"

        def _create():
            return client.containers.run(
                image,
                command="sleep infinity",
                detach=True,
                working_dir=spec.workdir,
                network_mode="bridge" if spec.network else "none",
                mem_limit=f"{spec.memory_mb}m",
                nano_cpus=int(spec.cpu_limit * 1_000_000_000),
                auto_remove=False,
            )

        self._container = await asyncio.to_thread(_create)
        await self._upload(instance.files)
        if spec.setup_script:
            code, out = await self.exec(spec.setup_script, timeout=spec.timeout_seconds)
            if code != 0:
                raise RuntimeError(f"setup_script failed ({code}): {out[:2000]}")

    async def _upload(self, files: dict[str, str]) -> None:
        if not files:
            return
        buf = BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as tar, tempfile.TemporaryDirectory() as tmp:
            for rel, content in files.items():
                p = Path(tmp) / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content)
                tar.add(p, arcname=rel)
        buf.seek(0)
        await asyncio.to_thread(self._require().put_archive, self._workdir, buf.read())

    def _require(self):
        if self._container is None:
            raise RuntimeError("sandbox not started")
        return self._container

    async def exec(self, command: str, timeout: int = 120) -> tuple[int, str]:
        def _run():
            return self._require().exec_run(
                ["/bin/sh", "-c", command], workdir=self._workdir, demux=False
            )

        try:
            result = await asyncio.wait_for(asyncio.to_thread(_run), timeout=timeout)
        except TimeoutError:
            return 124, f"timeout after {timeout}s"
        output = result.output
        if not isinstance(output, bytes):
            # demux=False should give bytes, but the SDK returns a stream in some modes.
            output = b"".join(output)
        return result.exit_code or 0, output.decode(errors="replace")

    async def read_file(self, path: str) -> str:
        code, out = await self.exec(f"cat {shlex.quote(path)}")
        if code != 0:
            raise FileNotFoundError(path)
        return out

    async def write_file(self, path: str, content: str) -> None:
        await self._upload({path: content})

    async def list_files(self, path: str = ".") -> list[str]:
        _, out = await self.exec(f"find {shlex.quote(path)} -type f")
        # `find .` emits "./name"; LocalSandbox emits "name". Verifiers look files up by
        # name, so an unnormalized prefix here makes every lookup miss silently — the whole
        # rollout scores zero and looks like a defeated agent rather than a broken harness.
        return sorted(
            stripped.removeprefix("./")
            for line in out.splitlines()
            if (stripped := line.strip())
        )

    async def stop(self) -> None:
        if self._container is None:
            return
        container = self._container
        self._container = None
        await asyncio.to_thread(container.remove, force=True)

"""Sandbox backends. Docker is the default; local is test-only and unisolated."""

from ef.core.types import SandboxSpec
from ef.sandbox.docker import DockerSandbox
from ef.sandbox.local import LocalSandbox

__all__ = ["DockerSandbox", "LocalSandbox", "build_sandbox"]


def build_sandbox(spec: SandboxSpec):
    """Instantiate the backend named by a SandboxSpec."""
    if spec.backend == "docker":
        return DockerSandbox()
    if spec.backend == "local":
        return LocalSandbox()
    raise NotImplementedError(
        f"backend {spec.backend!r} not implemented yet; use 'docker' or 'local'"
    )

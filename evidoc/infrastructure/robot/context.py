from __future__ import annotations

from contextvars import ContextVar

from evidoc.application.execution_service import ExecutionService

CURRENT_RUNTIME: ContextVar[ExecutionService | None] = ContextVar("CURRENT_RUNTIME", default=None)


def set_runtime(runtime: ExecutionService | None) -> None:
    CURRENT_RUNTIME.set(runtime)


def get_runtime() -> ExecutionService | None:
    return CURRENT_RUNTIME.get()

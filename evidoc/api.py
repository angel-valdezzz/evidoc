from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from evidoc.domain.enums import ArtifactType, Status
from evidoc.infrastructure.robot.context import get_runtime

LOGGER = logging.getLogger("evidoc.api")


def _runtime():
    runtime = get_runtime()
    if runtime is None:
        LOGGER.warning("Evidoc API was called without an active test context.")
    return runtime


def log_step(title: str, status: str = "INFO") -> None:
    runtime = _runtime()
    if runtime is None:
        return
    runtime.log_step(title, Status(status))


def capture_screenshot(
    driver: Any,
    element: Any | None = None,
    title: str | None = None,
    description: str | None = None,
) -> None:
    runtime = _runtime()
    if runtime is None:
        return
    runtime.capture_screenshot(driver, element=element, title=title, description=description)


def attach_artifact(path: str, description: str | None = None) -> None:
    runtime = _runtime()
    if runtime is None:
        return
    runtime.attach_artifact(Path(path), artifact_type=ArtifactType.FILE, description=description)


def log_info(message: str) -> None:
    runtime = _runtime()
    if runtime is None:
        return
    runtime.log_message(message, Status.INFO)


def log_warning(message: str) -> None:
    runtime = _runtime()
    if runtime is None:
        return
    runtime.log_message(message, Status.WARN)


def log_error(message: str) -> None:
    runtime = _runtime()
    if runtime is None:
        return
    runtime.log_message(message, Status.FAIL)

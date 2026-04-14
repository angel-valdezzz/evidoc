from __future__ import annotations

import logging
from contextvars import ContextVar
from pathlib import Path
from typing import Any, TypedDict

from evidoc.application.in_memory_warning_sink import InMemoryWarningSink
from evidoc.application.warning_sink import WarningSink
from evidoc.domain import run_from_dict
from evidoc.domain.artifact import Artifact
from evidoc.domain.artifact_type import ArtifactType
from evidoc.domain.status import Status
from evidoc.infrastructure.bootstrap import project_root
from evidoc.infrastructure.filesystem.filesystem_artifact_storage import FilesystemArtifactStorage
from evidoc.infrastructure.filesystem.filesystem_result_repository import FilesystemResultRepository

LOGGER = logging.getLogger("evidoc.api")


class ContextOptions(TypedDict):
    root_dir: Path | str
    result_schema_path: Path | None
    warning_sink: WarningSink | None


_CURRENT_API: ContextVar[EvidocAPI | None] = ContextVar("EVIDOC_CURRENT_API", default=None)
_CURRENT_OPTIONS: ContextVar[ContextOptions | None] = ContextVar(
    "EVIDOC_CURRENT_OPTIONS", default=None
)


class EvidocAPI:
    def __init__(
        self,
        *,
        root_dir: Path | str = Path("./results"),
        result_schema_path: Path | None = None,
        warning_sink: WarningSink | None = None,
    ) -> None:
        schema_path = result_schema_path or project_root() / "schemas" / "result.schema.json"
        self._root_dir = Path(root_dir)
        self._result_repository = FilesystemResultRepository(schema_path)
        self._artifact_storage = FilesystemArtifactStorage()
        self._warning_sink = warning_sink or InMemoryWarningSink()
        self._run_id: str | None = None
        self._current_test_name: str | None = None
        self._current_test_id: str | None = None
        self._steps: list[dict[str, Any]] = []
        self._artifacts: list[Artifact] = []

    @property
    def run_id(self) -> str | None:
        return self._run_id

    @property
    def test_id(self) -> str | None:
        return self._current_test_id

    @property
    def warnings(self) -> list[str]:
        messages = getattr(self._warning_sink, "messages", [])
        return list(messages)

    def start_test(self, test_name: str) -> str | None:
        try:
            if self._current_test_id is not None:
                self._warn("A previous test was still active. Closing it with WARN status.")
                self.end_test(Status.WARN, 0.0)
            self._run_id = self._result_repository.get_or_create_run_id(self._root_dir)
            self._current_test_id = self._generate_test_id()
            self._current_test_name = test_name or "Unnamed test"
            self._steps = []
            self._artifacts = []
            self._artifacts_dir().mkdir(parents=True, exist_ok=True)
            return self._current_test_id
        except Exception as exc:  # pragma: no cover
            self._warn(f"Unable to start test '{test_name}': {exc}")
            return None

    def end_test(self, status: str | Status, duration: float) -> str | None:
        try:
            if self._current_test_id is None or self._current_test_name is None:
                self._warn("No active test context to finish.")
                return None
            safe_status = self._coerce_status(status, fallback=Status.INFO)
            payload: dict[str, Any] = {
                "schema_version": "1.0.0",
                "run_id": self._run_id,
                "test_id": self._current_test_id,
                "generated_at": self._timestamp(),
                "test_case": {
                    "name": self._current_test_name,
                    "status": safe_status.value,
                    "duration": max(float(duration), 0.0),
                    "application": None,
                    "requirement": None,
                    "tags": [],
                },
                "steps": [
                    {
                        "title": step["title"],
                        "status": step["status"].value,
                        "logs": [
                            {
                                "level": log["level"].value,
                                "message": log["message"],
                                "timestamp": log["timestamp"],
                            }
                            for log in step["logs"]
                        ],
                        "artifact_ids": list(step["artifact_ids"]),
                    }
                    for step in self._steps
                ],
                "artifacts": [
                    {
                        "id": artifact.id,
                        "type": artifact.type.value,
                        "path": artifact.path,
                        "title": artifact.title,
                        "description": artifact.description,
                    }
                    for artifact in self._artifacts
                ],
            }
            result_path = self._result_repository.save_test_result(
                self._root_dir, run_from_dict(payload)
            )
            return str(result_path)
        except Exception as exc:  # pragma: no cover
            self._warn(f"Unable to finish test '{self._current_test_id}': {exc}")
            return None
        finally:
            self._current_test_name = None
            self._current_test_id = None
            self._steps = []
            self._artifacts = []

    def log_step(self, title: str, status: str | Status = Status.INFO) -> None:
        try:
            if self._current_test_id is None:
                self._warn(f"No active test context for step '{title}'.")
                return
            self._steps.append(
                {
                    "title": title or "Untitled step",
                    "status": self._coerce_status(status, fallback=Status.INFO),
                    "logs": [],
                    "artifact_ids": [],
                }
            )
        except Exception as exc:  # pragma: no cover
            self._warn(f"Unable to log step '{title}': {exc}")

    def log_info(self, message: str) -> None:
        self._log_message(message, Status.INFO)

    def log_warning(self, message: str) -> None:
        self._log_message(message, Status.WARN)

    def log_error(self, message: str) -> None:
        self._log_message(message, Status.FAIL)

    def capture_screenshot(
        self,
        driver: Any,
        element: Any | None = None,
        title: str | None = None,
        description: str | None = None,
    ) -> str | None:
        try:
            if self._current_test_id is None:
                self._warn("No active test context for screenshot capture.")
                return None
            target = element or driver
            destination = self._artifacts_dir() / f"screenshot-{self._generate_test_id()}.png"
            if hasattr(target, "screenshot"):
                if target.screenshot(str(destination)) is False:
                    raise RuntimeError("screenshot() returned False")
            elif hasattr(target, "save_screenshot"):
                if target.save_screenshot(str(destination)) is False:
                    raise RuntimeError("save_screenshot() returned False")
            else:
                raise TypeError("Driver does not support screenshot capture")
            return self._register_artifact(
                source_path=destination,
                artifact_type=ArtifactType.IMAGE,
                title=title or "Screenshot",
                description=description,
            )
        except Exception as exc:
            self._warn(f"Unable to capture screenshot: {exc}")
            return None

    def attach_file(self, path: str | Path, description: str | None = None) -> str | None:
        try:
            source_path = Path(path)
            if not source_path.exists():
                self._warn(f"Artifact '{source_path}' does not exist.")
                return None
            return self._register_artifact(
                source_path=source_path,
                artifact_type=ArtifactType.FILE,
                title=source_path.name,
                description=description,
            )
        except Exception as exc:  # pragma: no cover
            self._warn(f"Unable to attach file '{path}': {exc}")
            return None

    def _register_artifact(
        self,
        *,
        source_path: Path,
        artifact_type: ArtifactType,
        title: str | None,
        description: str | None,
    ) -> str | None:
        if self._current_test_id is None:
            self._warn(f"No active test context for artifact '{source_path}'.")
            return None
        artifact = self._artifact_storage.store_artifact(
            source_path=source_path,
            artifacts_dir=self._artifacts_dir(),
            artifact_type=artifact_type,
            title=title,
            description=description,
        )
        if artifact is None:
            self._warn(f"Artifact '{source_path}' was not attached.")
            return None
        self._artifacts.append(artifact)
        if not self._steps:
            self.log_step("Artifacts", Status.INFO)
        self._steps[-1]["artifact_ids"].append(artifact.id)
        return artifact.id

    def _log_message(self, message: str, level: Status) -> None:
        try:
            if self._current_test_id is None:
                self._warn(f"No active test context for log '{message}'.")
                return
            if not self._steps:
                self.log_step("Runtime messages", Status.INFO)
            self._steps[-1]["logs"].append(
                {
                    "level": level,
                    "message": message,
                    "timestamp": self._timestamp(),
                }
            )
        except Exception as exc:  # pragma: no cover
            self._warn(f"Unable to log message '{message}': {exc}")

    def _warn(self, message: str) -> None:
        try:
            self._warning_sink.warn(message)
        except Exception:  # pragma: no cover
            LOGGER.warning(message)

    def _test_dir(self) -> Path | None:
        if self._run_id is None or self._current_test_id is None:
            return None
        return self._root_dir / f"run-{self._run_id}" / f"test-{self._current_test_id}"

    def _artifacts_dir(self) -> Path:
        test_dir = self._test_dir()
        if test_dir is None:
            return self._root_dir / "artifacts"
        return test_dir / "artifacts"

    @staticmethod
    def _coerce_status(status: str | Status, *, fallback: Status) -> Status:
        try:
            return status if isinstance(status, Status) else Status(str(status).upper())
        except Exception:
            return fallback

    @staticmethod
    def _generate_test_id() -> str:
        from uuid import uuid4

        return str(uuid4())

    @staticmethod
    def _timestamp() -> str:
        from datetime import UTC, datetime

        return datetime.now(UTC).isoformat()


def configure_context(
    *,
    root_dir: Path | str = Path("./results"),
    result_schema_path: Path | None = None,
    warning_sink: WarningSink | None = None,
) -> EvidocAPI:
    options: ContextOptions = {
        "root_dir": Path(root_dir),
        "result_schema_path": result_schema_path,
        "warning_sink": warning_sink,
    }
    _CURRENT_OPTIONS.set(options)
    api = EvidocAPI(**options)
    _CURRENT_API.set(api)
    return api


def get_current_api() -> EvidocAPI:
    api = _CURRENT_API.get()
    if api is not None:
        return api
    options = _CURRENT_OPTIONS.get()
    api = EvidocAPI(**options) if options is not None else EvidocAPI()
    _CURRENT_API.set(api)
    return api


def clear_context() -> None:
    _CURRENT_API.set(None)


def start_test(test_name: str) -> str | None:
    return get_current_api().start_test(test_name)


def end_test(status: str | Status, duration: float) -> str | None:
    return get_current_api().end_test(status, duration)


def log_step(title: str, status: str | Status = Status.INFO) -> None:
    get_current_api().log_step(title, status)


def log_info(message: str) -> None:
    get_current_api().log_info(message)


def log_warning(message: str) -> None:
    get_current_api().log_warning(message)


def log_error(message: str) -> None:
    get_current_api().log_error(message)


def capture_screenshot(
    driver: Any,
    element: Any | None = None,
    title: str | None = None,
    description: str | None = None,
) -> str | None:
    return get_current_api().capture_screenshot(
        driver, element=element, title=title, description=description
    )


def attach_file(path: str | Path, description: str | None = None) -> str | None:
    return get_current_api().attach_file(path, description)


def attach_artifact(path: str | Path, description: str | None = None) -> str | None:
    return attach_file(path, description)

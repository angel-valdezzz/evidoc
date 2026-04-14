from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from evidoc.application.active_test_context import ActiveTestContext
from evidoc.application.artifact_storage import ArtifactStorage
from evidoc.application.result_repository import ResultRepository
from evidoc.application.warning_sink import WarningSink
from evidoc.domain.artifact import Artifact
from evidoc.domain.artifact_type import ArtifactType
from evidoc.domain.log_entry import LogEntry
from evidoc.domain.run import Run
from evidoc.domain.schema_version import SCHEMA_VERSION
from evidoc.domain.status import Status
from evidoc.domain.step import Step
from evidoc.domain.test_case import TestCase


class ExecutionService:
    schema_version = SCHEMA_VERSION

    def __init__(
        self,
        *,
        result_repository: ResultRepository,
        artifact_storage: ArtifactStorage,
        warning_sink: WarningSink,
        default_root_dir: Path = Path("./results"),
        default_application: str | None = None,
        default_requirement: str | None = None,
    ) -> None:
        self._result_repository = result_repository
        self._artifact_storage = artifact_storage
        self._warning_sink = warning_sink
        self._default_root_dir = default_root_dir
        self._default_application = default_application
        self._default_requirement = default_requirement
        self._current: ActiveTestContext | None = None

    def start_run(self, root_dir: Path | None = None) -> str:
        return self._result_repository.get_or_create_run_id(root_dir or self._default_root_dir)

    def start_test(
        self,
        name: str,
        *,
        root_dir: Path | None = None,
        application: str | None = None,
        requirement: str | None = None,
    ) -> str:
        root = root_dir or self._default_root_dir
        run_id = self.start_run(root)
        test_id = str(uuid4())
        self._current = ActiveTestContext(
            root_dir=root,
            run_id=run_id,
            test_id=test_id,
            name=name,
            application=application or self._default_application,
            requirement=requirement or self._default_requirement,
        )
        self._current.artifacts_dir.mkdir(parents=True, exist_ok=True)
        return test_id

    def current_test_id(self) -> str | None:
        return self._current.test_id if self._current else None

    def log_step(self, title: str, status: Status = Status.INFO) -> None:
        context = self._current
        if context is None:
            self._warning_sink.warn(f"No active test context for step '{title}'.")
            return
        context.steps.append({"title": title, "status": status, "logs": [], "artifact_ids": []})

    def log_message(self, message: str, level: Status) -> None:
        context = self._current
        if context is None:
            self._warning_sink.warn(f"No active test context for log '{message}'.")
            return
        if not context.steps:
            self.log_step("Runtime messages", Status.INFO)
        context.steps[-1]["logs"].append(LogEntry.create(level, message))

    def attach_artifact(
        self,
        source_path: str | Path,
        *,
        artifact_type: ArtifactType = ArtifactType.FILE,
        title: str | None = None,
        description: str | None = None,
    ) -> Artifact | None:
        context = self._current
        if context is None:
            self._warning_sink.warn(f"No active test context for artifact '{source_path}'.")
            return None
        try:
            artifact = self._artifact_storage.store_artifact(
                source_path=Path(source_path),
                artifacts_dir=context.artifacts_dir,
                artifact_type=artifact_type,
                title=title,
                description=description,
            )
        except Exception as exc:  # pragma: no cover
            self._warning_sink.warn(f"Unable to attach artifact '{source_path}': {exc}")
            return None
        if artifact is None:
            self._warning_sink.warn(f"Artifact '{source_path}' was not attached.")
            return None
        context.artifacts.append(artifact)
        if not context.steps:
            self.log_step("Artifacts", Status.INFO)
        context.steps[-1]["artifact_ids"].append(artifact.id)
        return artifact

    def capture_screenshot(
        self,
        driver: Any,
        *,
        element: Any | None = None,
        title: str | None = None,
        description: str | None = None,
    ) -> Artifact | None:
        context = self._current
        if context is None:
            self._warning_sink.warn("No active test context for screenshot capture.")
            return None
        target = element or driver
        destination = context.artifacts_dir / f"screenshot-{uuid4()}.png"
        try:
            if hasattr(target, "screenshot"):
                if target.screenshot(str(destination)) is False:
                    raise RuntimeError("screenshot() returned False")
            elif hasattr(target, "save_screenshot"):
                if target.save_screenshot(str(destination)) is False:
                    raise RuntimeError("save_screenshot() returned False")
            else:
                raise TypeError("Driver does not support screenshot capture")
        except Exception as exc:
            self._warning_sink.warn(f"Unable to capture screenshot: {exc}")
            return None
        return self.attach_artifact(
            destination,
            artifact_type=ArtifactType.IMAGE,
            title=title or "Screenshot",
            description=description,
        )

    def finish_test(self, status: Status, *, duration: float = 0.0) -> Run | None:
        context = self._current
        if context is None:
            self._warning_sink.warn("No active test context to finish.")
            return None
        result = Run(
            schema_version=self.schema_version,
            run_id=context.run_id,
            test_id=context.test_id,
            generated_at=datetime.now(UTC).isoformat(),
            test_case=TestCase(
                name=context.name,
                status=status,
                duration=duration,
                application=context.application,
                requirement=context.requirement,
            ),
            steps=tuple(
                Step(
                    title=step["title"],
                    status=step["status"],
                    logs=tuple(step["logs"]),
                    artifact_ids=tuple(step["artifact_ids"]),
                )
                for step in context.steps
            ),
            artifacts=tuple(context.artifacts),
        )
        try:
            self._result_repository.save_test_result(context.root_dir, result)
        except Exception as exc:  # pragma: no cover
            self._warning_sink.warn(f"Unable to persist test result '{context.test_id}': {exc}")
        self._current = None
        return result

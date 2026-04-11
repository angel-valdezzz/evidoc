from __future__ import annotations

import json
import shutil
from pathlib import Path
from uuid import uuid4

from jsonschema import validate

from evidoc.application.ports import ArtifactStorage, ResultRepository
from evidoc.domain.enums import ArtifactType, Status
from evidoc.domain.models import ArtifactRef, LogEntry, StepResult, TestCaseMetadata, TestResult


class FilesystemResultRepository(ResultRepository):
    def __init__(self, result_schema_path: Path) -> None:
        self._result_schema = json.loads(result_schema_path.read_text(encoding="utf-8"))

    def get_or_create_run_id(self, root_dir: Path) -> str:
        root_dir.mkdir(parents=True, exist_ok=True)
        run_id_file = root_dir / ".run_id"
        if run_id_file.exists():
            return run_id_file.read_text(encoding="utf-8").strip()
        run_id = uuid4().hex[:12]
        run_id_file.write_text(run_id, encoding="utf-8")
        return run_id

    def save_test_result(self, root_dir: Path, result: TestResult) -> Path:
        test_dir = root_dir / f"run-{result.run_id}" / f"test-{result.test_id}"
        test_dir.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        validate(payload, self._result_schema)
        result_path = test_dir / "result.json"
        result_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return result_path

    def load_test_results(self, source_dir: Path) -> list[TestResult]:
        if not source_dir.exists():
            return []
        results: list[TestResult] = []
        for result_path in sorted(source_dir.glob("run-*/test-*/result.json")):
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            validate(payload, self._result_schema)
            results.append(self._from_dict(payload))
        return results

    def _from_dict(self, payload: dict) -> TestResult:
        return TestResult(
            schema_version=payload["schema_version"],
            run_id=payload["run_id"],
            test_id=payload["test_id"],
            generated_at=payload["generated_at"],
            test_case=TestCaseMetadata(
                name=payload["test_case"]["name"],
                status=Status(payload["test_case"]["status"]),
                duration=payload["test_case"]["duration"],
                application=payload["test_case"].get("application"),
                requirement=payload["test_case"].get("requirement"),
            ),
            steps=tuple(
                StepResult(
                    title=step["title"],
                    status=Status(step["status"]),
                    logs=tuple(
                        LogEntry(
                            level=Status(log["level"]),
                            message=log["message"],
                            timestamp=log["timestamp"],
                        )
                        for log in step.get("logs", [])
                    ),
                    artifact_ids=tuple(step.get("artifact_ids", [])),
                )
                for step in payload.get("steps", [])
            ),
            artifacts=tuple(
                ArtifactRef(
                    id=artifact["id"],
                    type=ArtifactType(artifact["type"]),
                    path=artifact["path"],
                    title=artifact.get("title"),
                    description=artifact.get("description"),
                )
                for artifact in payload.get("artifacts", [])
            ),
        )


class FilesystemArtifactStorage(ArtifactStorage):
    def store_artifact(
        self,
        *,
        source_path: Path,
        artifacts_dir: Path,
        artifact_type: ArtifactType,
        title: str | None = None,
        description: str | None = None,
    ) -> ArtifactRef | None:
        if not source_path.exists():
            return None
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        if source_path.parent.resolve() == artifacts_dir.resolve():
            destination = source_path
            artifact_id = source_path.stem
        else:
            artifact_id = uuid4().hex
            destination = artifacts_dir / f"{artifact_id}{source_path.suffix or ''}"
            if source_path.resolve() != destination.resolve():
                shutil.copy2(source_path, destination)
        relative_path = destination.relative_to(artifacts_dir.parent).as_posix()
        return ArtifactRef(
            id=artifact_id,
            type=artifact_type,
            path=relative_path,
            title=title,
            description=description,
        )

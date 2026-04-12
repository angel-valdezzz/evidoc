from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from jsonschema import validate

from evidoc.application.result_repository import ResultRepository
from evidoc.domain.artifact import Artifact
from evidoc.domain.artifact_type import ArtifactType
from evidoc.domain.log_entry import LogEntry
from evidoc.domain.run import Run
from evidoc.domain.status import Status
from evidoc.domain.step import Step
from evidoc.domain.test_case import TestCase


class FilesystemResultRepository(ResultRepository):
    def __init__(self, result_schema_path: Path) -> None:
        self._result_schema = json.loads(result_schema_path.read_text(encoding="utf-8"))

    def get_or_create_run_id(self, root_dir: Path) -> str:
        root_dir.mkdir(parents=True, exist_ok=True)
        run_id_file = root_dir / ".run_id"
        if run_id_file.exists():
            return run_id_file.read_text(encoding="utf-8").strip()
        run_id = uuid4().hex[:12]
        try:
            with run_id_file.open("x", encoding="utf-8") as handle:
                handle.write(run_id)
            return run_id
        except FileExistsError:
            return run_id_file.read_text(encoding="utf-8").strip()

    def save_test_result(self, root_dir: Path, result: Run) -> Path:
        test_dir = root_dir / f"run-{result.run_id}" / f"test-{result.test_id}"
        test_dir.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        validate(payload, self._result_schema)
        result_path = test_dir / "result.json"
        result_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return result_path

    def load_test_results(self, source_dir: Path) -> list[Run]:
        if not source_dir.exists():
            return []
        results: list[Run] = []
        for result_path in sorted(source_dir.glob("run-*/test-*/result.json")):
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            validate(payload, self._result_schema)
            results.append(self._from_dict(payload))
        return results

    def _from_dict(self, payload: dict) -> Run:
        return Run(
            schema_version=payload["schema_version"],
            run_id=payload["run_id"],
            test_id=payload["test_id"],
            generated_at=payload["generated_at"],
            test_case=TestCase(
                name=payload["test_case"]["name"],
                status=Status(payload["test_case"]["status"]),
                duration=payload["test_case"]["duration"],
                application=payload["test_case"].get("application"),
                requirement=payload["test_case"].get("requirement"),
            ),
            steps=tuple(
                Step(
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
                Artifact(
                    id=artifact["id"],
                    type=ArtifactType(artifact["type"]),
                    path=artifact["path"],
                    title=artifact.get("title"),
                    description=artifact.get("description"),
                )
                for artifact in payload.get("artifacts", [])
            ),
        )

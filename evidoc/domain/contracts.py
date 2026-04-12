from __future__ import annotations

import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from evidoc.domain.enums import ArtifactType, Status
from evidoc.domain.models import Artifact, LogEntry, Run, Step, TestCase


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def load_run_schema() -> dict[str, Any]:
    schema_path = _project_root() / "schemas" / "result.schema.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def get_run_validator() -> Draft202012Validator:
    return Draft202012Validator(load_run_schema())


def validate_run_payload(payload: dict[str, Any]) -> None:
    validator = get_run_validator()
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.absolute_path))
    if errors:
        raise errors[0]

    artifact_ids = [artifact["id"] for artifact in payload.get("artifacts", [])]
    duplicates = {artifact_id for artifact_id, count in Counter(artifact_ids).items() if count > 1}
    if duplicates:
        joined = ", ".join(sorted(duplicates))
        raise ValueError(f"Duplicate artifact IDs are not allowed: {joined}")

    known_ids = set(artifact_ids)
    dangling_ids = sorted(
        {
            artifact_id
            for step in payload.get("steps", [])
            for artifact_id in step.get("artifact_ids", [])
            if artifact_id not in known_ids
        }
    )
    if dangling_ids:
        joined = ", ".join(dangling_ids)
        raise ValueError(f"Artifact references must point to globally defined artifacts: {joined}")


def validate_run(run: Run) -> None:
    validate_run_payload(run.to_dict())


def run_from_dict(payload: dict[str, Any]) -> Run:
    validate_run_payload(payload)
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
            tags=tuple(payload["test_case"].get("tags", [])),
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

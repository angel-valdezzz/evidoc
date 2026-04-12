from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from evidoc.domain.artifact import Artifact
from evidoc.domain.step import Step
from evidoc.domain.test_case import TestCase


@dataclass(frozen=True, slots=True)
class Run:
    schema_version: str
    run_id: str
    test_id: str
    generated_at: str
    test_case: TestCase
    steps: tuple[Step, ...]
    artifacts: tuple[Artifact, ...] = ()

    def __post_init__(self) -> None:
        artifact_ids = [artifact.id for artifact in self.artifacts]
        duplicate_ids = {artifact_id for artifact_id, count in Counter(artifact_ids).items() if count > 1}
        if duplicate_ids:
            joined = ", ".join(sorted(duplicate_ids))
            raise ValueError(f"Duplicate artifact IDs are not allowed: {joined}")

        known_ids = set(artifact_ids)
        dangling_ids = sorted(
            {
                artifact_id
                for step in self.steps
                for artifact_id in step.artifact_ids
                if artifact_id not in known_ids
            }
        )
        if dangling_ids:
            joined = ", ".join(dangling_ids)
            raise ValueError(f"Every artifact reference must resolve to a globally declared artifact: {joined}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "test_id": self.test_id,
            "generated_at": self.generated_at,
            "test_case": {
                "name": self.test_case.name,
                "status": self.test_case.status.value,
                "duration": self.test_case.duration,
                "application": self.test_case.application,
                "requirement": self.test_case.requirement,
                "tags": list(self.test_case.tags),
            },
            "steps": [
                {
                    "title": step.title,
                    "status": step.status.value,
                    "logs": [
                        {
                            "level": log.level.value,
                            "message": log.message,
                            "timestamp": log.timestamp,
                        }
                        for log in step.logs
                    ],
                    "artifact_ids": list(step.artifact_ids),
                }
                for step in self.steps
            ],
            "artifacts": [
                {
                    "id": artifact.id,
                    "type": artifact.type.value,
                    "path": artifact.path,
                    "title": artifact.title,
                    "description": artifact.description,
                }
                for artifact in self.artifacts
            ],
        }

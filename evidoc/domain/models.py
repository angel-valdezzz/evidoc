from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ClassVar

from evidoc.domain.enums import ArtifactType, GenerateMode, ReportFormat, Status

SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class RunId:
    value: str


@dataclass(frozen=True, slots=True)
class TestId:
    value: str


@dataclass(frozen=True, slots=True)
class ArtifactId:
    value: str


@dataclass(frozen=True, slots=True)
class LogEntry:
    level: Status
    message: str
    timestamp: str

    @classmethod
    def create(cls, level: Status, message: str) -> "LogEntry":
        return cls(level=level, message=message, timestamp=datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True, slots=True)
class Artifact:
    id: str
    type: ArtifactType
    path: str
    title: str | None = None
    description: str | None = None


@dataclass(frozen=True, slots=True)
class Step:
    title: str
    status: Status
    logs: tuple[LogEntry, ...] = ()
    artifact_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TestCase:
    __test__: ClassVar[bool] = False

    name: str
    status: Status
    duration: float
    application: str | None = None
    requirement: str | None = None
    tags: tuple[str, ...] = ()


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


@dataclass(frozen=True, slots=True)
class RunManifest:
    run_id: str
    root_dir: Path
    tests: tuple[Run, ...] = ()


@dataclass(frozen=True, slots=True)
class EvidocConfig:
    source_dir: Path = Path("./results")
    output_dir: Path = Path("./reports")
    format: ReportFormat = ReportFormat.PDF
    mode: GenerateMode = GenerateMode.RUN
    application: str | None = None
    requirement: str | None = None
    config_path: Path | None = None

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "EvidocConfig":
        source_dir = Path(payload.get("source_dir", "./results"))
        output_dir = Path(payload.get("output_dir", "./reports"))
        fmt = ReportFormat(payload.get("format", ReportFormat.PDF))
        mode = GenerateMode(payload.get("mode", GenerateMode.RUN))
        config_path = payload.get("config_path")
        return cls(
            source_dir=source_dir,
            output_dir=output_dir,
            format=fmt,
            mode=mode,
            application=payload.get("application"),
            requirement=payload.get("requirement"),
            config_path=Path(config_path) if config_path else None,
        )


# Backward-compatible aliases for the broader scaffold already present in the repo.
ArtifactRef = Artifact
StepResult = Step
TestCaseMetadata = TestCase
TestResult = Run

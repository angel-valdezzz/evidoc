from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from evidoc.domain.enums import ArtifactType, GenerateMode, ReportFormat, Status


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
        return cls(level=level, message=message, timestamp=datetime.utcnow().isoformat())


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    id: str
    type: ArtifactType
    path: str
    title: str | None = None
    description: str | None = None


@dataclass(frozen=True, slots=True)
class StepResult:
    title: str
    status: Status
    logs: tuple[LogEntry, ...] = ()
    artifact_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TestCaseMetadata:
    name: str
    status: Status
    duration: float
    application: str | None = None
    requirement: str | None = None


@dataclass(frozen=True, slots=True)
class TestResult:
    schema_version: str
    run_id: str
    test_id: str
    generated_at: str
    test_case: TestCaseMetadata
    steps: tuple[StepResult, ...]
    artifacts: tuple[ArtifactRef, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RunManifest:
    run_id: str
    root_dir: Path
    tests: tuple[TestResult, ...] = ()


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

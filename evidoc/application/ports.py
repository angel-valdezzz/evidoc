from __future__ import annotations

from pathlib import Path
from typing import Protocol

from evidoc.domain.enums import ArtifactType
from evidoc.domain.models import ArtifactRef, TestResult


class WarningSink(Protocol):
    def warn(self, message: str) -> None: ...


class ResultRepository(Protocol):
    def get_or_create_run_id(self, root_dir: Path) -> str: ...
    def save_test_result(self, root_dir: Path, result: TestResult) -> Path: ...
    def load_test_results(self, source_dir: Path) -> list[TestResult]: ...


class ArtifactStorage(Protocol):
    def store_artifact(
        self,
        *,
        source_path: Path,
        artifacts_dir: Path,
        artifact_type: ArtifactType,
        title: str | None = None,
        description: str | None = None,
    ) -> ArtifactRef | None: ...


class ConfigRepository(Protocol):
    def load(self, config_path: Path | None = None) -> dict: ...


class ReportRenderer(Protocol):
    format_name: str

    def render_single(self, source_dir: Path, output_dir: Path, result: TestResult) -> Path: ...
    def render_run(self, source_dir: Path, output_dir: Path, results: list[TestResult]) -> Path: ...

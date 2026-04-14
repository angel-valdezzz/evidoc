from __future__ import annotations

import re
from pathlib import Path

import pytest
from evidoc.application.services import GenerateReportUseCase
from evidoc.domain.enums import ArtifactType, GenerateMode, ReportFormat, Status
from evidoc.domain.models import (
    ArtifactRef,
    LogEntry,
    StepResult,
)
from evidoc.domain.models import (
    TestCaseMetadata as CaseMeta,
)
from evidoc.domain.models import (
    TestResult as ResultModel,
)
from evidoc.infrastructure.bootstrap import project_root
from evidoc.infrastructure.filesystem.repository import FilesystemResultRepository
from evidoc.infrastructure.reporting.docx_renderer import DocxReportRenderer
from evidoc.infrastructure.reporting.pdf_renderer import PdfReportRenderer
from evidoc.interfaces.cli.main import app
from PIL import Image as PilImage
from typer.testing import CliRunner

pytestmark = pytest.mark.unit

RUNNER = CliRunner()


def build_result(
    *, run_id: str, test_id: str, image_count: int = 0, include_missing_image: bool = False
) -> ResultModel:
    artifact_ids = []
    artifacts = []
    for index in range(image_count):
        artifact_id = f"img_{index + 1}"
        artifact_ids.append(artifact_id)
        artifacts.append(
            ArtifactRef(
                id=artifact_id,
                type=ArtifactType.IMAGE,
                path=f"artifacts/{artifact_id}.png",
                title=f"Screenshot {index + 1}",
                description=f"Captured state {index + 1}.",
            )
        )

    if include_missing_image:
        artifact_ids.append("missing_image")
        artifacts.append(
            ArtifactRef(
                id="missing_image",
                type=ArtifactType.IMAGE,
                path="artifacts/missing.png",
                title="Missing screenshot",
                description="This file should be reported as missing.",
            )
        )

    artifacts.append(
        ArtifactRef(
            id="run_log",
            type=ArtifactType.LOG,
            path="artifacts/network-log.json",
            title="Network log",
            description="Sanitized request log.",
        )
    )

    return ResultModel(
        schema_version="1.0.0",
        run_id=run_id,
        test_id=test_id,
        generated_at="2026-04-11T23:03:17Z",
        test_case=CaseMeta(
            name=f"Test {test_id}",
            status=Status.FAIL if include_missing_image else Status.PASS,
            duration=1.25,
            application="Evidence Portal",
            requirement="REQ-123",
        ),
        steps=(
            StepResult(
                title="Open page",
                status=Status.PASS,
                logs=(
                    LogEntry(
                        level=Status.INFO,
                        message="Navigated to the page",
                        timestamp="2026-04-11T23:03:06Z",
                    ),
                ),
                artifact_ids=tuple(artifact_ids[: max(1, len(artifact_ids))]),
            ),
            StepResult(
                title="Validate content",
                status=Status.FAIL if include_missing_image else Status.PASS,
                logs=(
                    LogEntry(
                        level=Status.INFO,
                        message="Collected validation logs",
                        timestamp="2026-04-11T23:03:12Z",
                    ),
                    LogEntry(
                        level=Status.WARN if include_missing_image else Status.INFO,
                        message="Attached secondary evidence",
                        timestamp="2026-04-11T23:03:13Z",
                    ),
                ),
                artifact_ids=("run_log",),
            ),
        ),
        artifacts=tuple(artifacts),
    )


def persist_result(root_dir: Path, result: ResultModel) -> None:
    repo = FilesystemResultRepository(project_root() / "schemas" / "result.schema.json")
    repo.save_test_result(root_dir, result)
    test_dir = root_dir / f"run-{result.run_id}" / f"test-{result.test_id}"
    for artifact in result.artifacts:
        if artifact.type == ArtifactType.IMAGE and "missing" not in artifact.id:
            artifact_path = test_dir / Path(artifact.path)
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            PilImage.new("RGB", (32, 24), color=(25, 118, 210)).save(artifact_path, format="PNG")
        elif artifact.type != ArtifactType.IMAGE:
            artifact_path = test_dir / Path(artifact.path)
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text('{"ok": true}', encoding="utf-8")


def pdf_page_count(path: Path) -> int:
    return len(re.findall(rb"/Type\s*/Page\b", path.read_bytes()))


def test_cli_generate_single_creates_one_pdf_per_test(tmp_path: Path) -> None:
    persist_result(tmp_path / "results", build_result(run_id="run_cli", test_id="case_1"))
    persist_result(tmp_path / "results", build_result(run_id="run_cli", test_id="case_2"))

    result = RUNNER.invoke(
        app,
        [
            "generate",
            "--source_dir",
            str(tmp_path / "results"),
            "--output_dir",
            str(tmp_path / "reports"),
            "--mode",
            "single",
        ],
    )

    assert result.exit_code == 0, result.stdout
    outputs = sorted((tmp_path / "reports").glob("*.pdf"))
    assert len(outputs) == 2


def test_cli_generate_run_creates_single_combined_pdf(tmp_path: Path) -> None:
    persist_result(tmp_path / "results", build_result(run_id="run_cli", test_id="case_1"))
    persist_result(tmp_path / "results", build_result(run_id="run_cli", test_id="case_2"))

    result = RUNNER.invoke(
        app,
        [
            "generate",
            "--source_dir",
            str(tmp_path / "results"),
            "--output_dir",
            str(tmp_path / "reports"),
            "--mode",
            "run",
        ],
    )

    assert result.exit_code == 0, result.stdout
    outputs = sorted((tmp_path / "reports").glob("*.pdf"))
    assert len(outputs) == 1
    assert outputs[0].name == "run-run_cli.pdf"


def test_cli_generate_single_creates_docx_when_requested(tmp_path: Path) -> None:
    persist_result(tmp_path / "results", build_result(run_id="run_cli_docx", test_id="case_1"))

    result = RUNNER.invoke(
        app,
        [
            "generate",
            "--source_dir",
            str(tmp_path / "results"),
            "--output_dir",
            str(tmp_path / "reports"),
            "--mode",
            "single",
            "--format",
            "docx",
        ],
    )

    assert result.exit_code == 0, result.stdout
    outputs = sorted((tmp_path / "reports").glob("*.docx"))
    assert len(outputs) == 1


def test_pdf_renderer_handles_images_missing_images_and_pagination(tmp_path: Path) -> None:
    source_dir = tmp_path / "results"
    output_dir = tmp_path / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    result = build_result(
        run_id="run_pdf", test_id="case_pdf", image_count=3, include_missing_image=True
    )
    persist_result(source_dir, result)

    output_path = PdfReportRenderer().render_run(source_dir, output_dir, [result])

    assert output_path.exists()
    assert pdf_page_count(output_path) >= 2


def test_generate_report_use_case_still_supports_pdf_output(tmp_path: Path) -> None:
    persist_result(tmp_path / "results", build_result(run_id="run_use_case", test_id="case_pdf"))

    repo = FilesystemResultRepository(project_root() / "schemas" / "result.schema.json")
    pdf_outputs = GenerateReportUseCase(
        repo,
        {ReportFormat.PDF: PdfReportRenderer()},
    ).execute(
        type(
            "Cfg",
            (),
            {
                "source_dir": tmp_path / "results",
                "output_dir": tmp_path / "reports-pdf",
                "format": ReportFormat.PDF,
                "mode": GenerateMode.RUN,
            },
        )()
    )

    assert pdf_outputs[0].exists()


def test_generate_report_use_case_supports_docx_output(tmp_path: Path) -> None:
    persist_result(
        tmp_path / "results", build_result(run_id="run_use_case_docx", test_id="case_docx")
    )

    repo = FilesystemResultRepository(project_root() / "schemas" / "result.schema.json")
    docx_outputs = GenerateReportUseCase(
        repo,
        {ReportFormat.DOCX: DocxReportRenderer()},
    ).execute(
        type(
            "Cfg",
            (),
            {
                "source_dir": tmp_path / "results",
                "output_dir": tmp_path / "reports-docx",
                "format": ReportFormat.DOCX,
                "mode": GenerateMode.RUN,
            },
        )()
    )

    assert docx_outputs[0].exists()
    assert docx_outputs[0].suffix == ".docx"


def test_cli_docs_without_subcommand_lists_available_targets() -> None:
    result = RUNNER.invoke(app, ["docs"])

    assert result.exit_code == 0
    assert "Available targets: manual, robot-library" in result.stdout


def test_cli_docs_manual_opens_bundled_mkdocs_site(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    document_path = tmp_path / "site" / "index.html"
    document_path.parent.mkdir(parents=True, exist_ok=True)
    document_path.write_text("<html></html>", encoding="utf-8")
    opened: list[str] = []

    def fake_open_documentation(name: str) -> Path:
        opened.append(name)
        return document_path

    monkeypatch.setattr("evidoc.interfaces.cli.main.open_documentation", fake_open_documentation)

    result = RUNNER.invoke(app, ["docs", "manual"])

    assert result.exit_code == 0, result.stdout
    assert opened == ["manual"]
    assert str(document_path) in result.stdout


def test_cli_docs_robot_library_opens_bundled_reference(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    document_path = tmp_path / "robot-library.html"
    document_path.write_text("<html></html>", encoding="utf-8")
    opened: list[str] = []

    def fake_open_documentation(name: str) -> Path:
        opened.append(name)
        return document_path

    monkeypatch.setattr("evidoc.interfaces.cli.main.open_documentation", fake_open_documentation)

    result = RUNNER.invoke(app, ["docs", "robot-library"])

    assert result.exit_code == 0, result.stdout
    assert opened == ["robot-library"]
    assert str(document_path) in result.stdout

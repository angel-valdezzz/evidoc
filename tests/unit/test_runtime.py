from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import validate

from evidoc.application.services import ExecutionService, GenerateReportUseCase, InMemoryWarningSink, LoadConfigUseCase
from evidoc.domain.enums import GenerateMode, ReportFormat, Status
from evidoc.infrastructure.bootstrap import project_root
from evidoc.infrastructure.config.repository import SchemaValidatedConfigRepository
from evidoc.infrastructure.filesystem.repository import FilesystemArtifactStorage, FilesystemResultRepository
from evidoc.infrastructure.reporting.docx_renderer import DocxReportRenderer
from evidoc.infrastructure.reporting.pdf_renderer import PdfReportRenderer
from evidoc.listener import Listener

pytestmark = pytest.mark.unit


def build_runtime(tmp_path: Path) -> tuple[ExecutionService, InMemoryWarningSink]:
    sink = InMemoryWarningSink()
    repo = FilesystemResultRepository(project_root() / "schemas" / "result.schema.json")
    runtime = ExecutionService(
        result_repository=repo,
        artifact_storage=FilesystemArtifactStorage(),
        warning_sink=sink,
        default_root_dir=tmp_path / "results",
    )
    return runtime, sink


def test_run_id_is_reused(tmp_path: Path) -> None:
    runtime, _ = build_runtime(tmp_path)
    assert runtime.start_run() == runtime.start_run()


def test_unique_test_ids_and_json_contract(tmp_path: Path) -> None:
    runtime, _ = build_runtime(tmp_path)
    attachment = tmp_path / "attachment.txt"
    attachment.write_text("hello", encoding="utf-8")
    first = runtime.start_test("First")
    runtime.log_step("Step one", Status.PASS)
    runtime.attach_artifact(attachment)
    runtime.finish_test(Status.PASS, duration=1.2)
    second = runtime.start_test("Second")
    runtime.finish_test(Status.FAIL, duration=0.3)
    assert first != second
    result_path = next((tmp_path / "results").glob("run-*/test-*/result.json"))
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    schema = json.loads((project_root() / "schemas" / "result.schema.json").read_text(encoding="utf-8"))
    validate(payload, schema)
    assert "artifact_ids" in payload["steps"][0]
    assert "artifacts" not in payload["steps"][0]


def test_missing_artifact_produces_warning(tmp_path: Path) -> None:
    runtime, sink = build_runtime(tmp_path)
    runtime.start_test("Warning case")
    runtime.attach_artifact(tmp_path / "missing.txt")
    runtime.finish_test(Status.WARN, duration=0.1)
    assert sink.messages


def test_config_precedence(tmp_path: Path) -> None:
    config_path = tmp_path / "evidoc.toml"
    config_path.write_text('source_dir = "./custom-results"\nformat = "docx"\nmode = "single"\n', encoding="utf-8")
    repo = SchemaValidatedConfigRepository(project_root() / "schemas" / "config.schema.json")
    config = LoadConfigUseCase(repo).execute(config_path, overrides={"format": "pdf"})
    assert config.source_dir == Path("./custom-results")
    assert config.format == ReportFormat.PDF
    assert config.mode == GenerateMode.SINGLE


def test_generate_pdf_and_docx_reports(tmp_path: Path) -> None:
    runtime, _ = build_runtime(tmp_path)
    runtime.start_test("Render me")
    runtime.log_step("Step", Status.PASS)
    runtime.finish_test(Status.PASS, duration=0.2)
    repo = FilesystemResultRepository(project_root() / "schemas" / "result.schema.json")
    pdf_outputs = GenerateReportUseCase(repo, {ReportFormat.PDF: PdfReportRenderer()}).execute(
        type("Cfg", (), {"source_dir": tmp_path / "results", "output_dir": tmp_path / "reports-pdf", "format": ReportFormat.PDF, "mode": GenerateMode.RUN})()
    )
    docx_outputs = GenerateReportUseCase(repo, {ReportFormat.DOCX: DocxReportRenderer()}).execute(
        type("Cfg", (), {"source_dir": tmp_path / "results", "output_dir": tmp_path / "reports-docx", "format": ReportFormat.DOCX, "mode": GenerateMode.SINGLE})()
    )
    assert pdf_outputs[0].exists()
    assert docx_outputs[0].exists()


def test_screenshot_failure_does_not_break_execution(tmp_path: Path) -> None:
    runtime, sink = build_runtime(tmp_path)
    runtime.start_test("Screenshot warning")

    class Driver:
        def save_screenshot(self, path: str) -> bool:
            return False

    runtime.capture_screenshot(Driver(), title="broken")
    runtime.finish_test(Status.INFO, duration=0.1)
    assert any("Unable to capture screenshot" in message for message in sink.messages)


def test_listener_creates_result_for_active_test(tmp_path: Path, monkeypatch) -> None:
    runtime, _ = build_runtime(tmp_path)
    monkeypatch.setattr("evidoc.listener.build_runtime", lambda: runtime)
    listener = Listener()
    data = type("Data", (), {"name": "Robot test"})()
    result = type("Result", (), {"status": "PASS"})()
    listener.start_test(data, result)
    listener.end_test(data, result)
    assert list((tmp_path / "results").glob("run-*/test-*/result.json"))

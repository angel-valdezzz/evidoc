from __future__ import annotations

from pathlib import Path

from evidoc.application.services import ExecutionService, GenerateReportUseCase, LoadConfigUseCase
from evidoc.domain.enums import ReportFormat
from evidoc.infrastructure.config.repository import SchemaValidatedConfigRepository
from evidoc.infrastructure.filesystem.repository import FilesystemArtifactStorage, FilesystemResultRepository
from evidoc.infrastructure.logging import LoggerWarningSink
from evidoc.infrastructure.reporting.docx_renderer import DocxReportRenderer
from evidoc.infrastructure.reporting.pdf_renderer import PdfReportRenderer


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_runtime(
    *,
    root_dir: Path = Path("./results"),
    application: str | None = None,
    requirement: str | None = None,
) -> ExecutionService:
    base = project_root()
    return ExecutionService(
        result_repository=FilesystemResultRepository(base / "schemas" / "result.schema.json"),
        artifact_storage=FilesystemArtifactStorage(),
        warning_sink=LoggerWarningSink(),
        default_root_dir=root_dir,
        default_application=application,
        default_requirement=requirement,
    )


def build_generate_use_case() -> tuple[LoadConfigUseCase, GenerateReportUseCase]:
    base = project_root()
    config_repo = SchemaValidatedConfigRepository(base / "schemas" / "config.schema.json")
    result_repo = FilesystemResultRepository(base / "schemas" / "result.schema.json")
    renderers = {
        ReportFormat.PDF: PdfReportRenderer(),
        ReportFormat.DOCX: DocxReportRenderer(),
    }
    return LoadConfigUseCase(config_repo), GenerateReportUseCase(result_repo, renderers)

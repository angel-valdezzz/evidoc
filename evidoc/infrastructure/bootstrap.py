from __future__ import annotations

from pathlib import Path

from evidoc.application.execution_service import ExecutionService
from evidoc.application.generate_report_use_case import GenerateReportUseCase
from evidoc.application.load_config_use_case import LoadConfigUseCase
from evidoc.domain.report_format import ReportFormat
from evidoc.infrastructure.config.repository import SchemaValidatedConfigRepository
from evidoc.infrastructure.filesystem.filesystem_artifact_storage import FilesystemArtifactStorage
from evidoc.infrastructure.filesystem.filesystem_result_repository import FilesystemResultRepository
from evidoc.infrastructure.logging import LoggerWarningSink
from evidoc.infrastructure.reporting.docx_renderer import DocxReportRenderer
from evidoc.infrastructure.reporting.pdf_renderer import PdfReportRenderer
from evidoc.schema_paths import config_schema_path, result_schema_path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_runtime(
    *,
    root_dir: Path = Path("./results"),
    application: str | None = None,
    requirement: str | None = None,
) -> ExecutionService:
    return ExecutionService(
        result_repository=FilesystemResultRepository(result_schema_path()),
        artifact_storage=FilesystemArtifactStorage(),
        warning_sink=LoggerWarningSink(),
        default_root_dir=root_dir,
        default_application=application,
        default_requirement=requirement,
    )


def build_generate_use_case() -> tuple[LoadConfigUseCase, GenerateReportUseCase]:
    config_repo = SchemaValidatedConfigRepository(config_schema_path())
    result_repo = FilesystemResultRepository(result_schema_path())
    renderers = {
        ReportFormat.PDF: PdfReportRenderer(),
        ReportFormat.DOCX: DocxReportRenderer(),
    }
    return LoadConfigUseCase(config_repo), GenerateReportUseCase(result_repo, renderers)

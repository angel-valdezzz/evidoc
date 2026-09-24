from pathlib import Path

from evidoc.application.report_filename import safe_name
from evidoc.application.report_renderer import ReportRenderer
from evidoc.application.result_repository import ResultRepository
from evidoc.domain.evidoc_config import EvidocConfig
from evidoc.domain.report_format import ReportFormat


class GenerateReportUseCase:
    def __init__(
        self, result_repository: ResultRepository, renderers: dict[ReportFormat, ReportRenderer]
    ) -> None:
        self._result_repository = result_repository
        self._renderers = renderers

    def execute(self, config: EvidocConfig) -> list[Path]:
        renderer = self._renderers[config.format]
        results = self._result_repository.load_test_results(config.source_dir)
        if not results:
            return []
        if config.mode.value == "single":
            names = [safe_name(result.test_case.name).casefold() for result in results]
            if len(names) != len(set(names)):
                raise ValueError(
                    "Case names must be unique within the metadata directory to generate "
                    "reports without overwriting files. Use separate metadata directories "
                    "for separate runs."
                )
        config.output_dir.mkdir(parents=True, exist_ok=True)
        if config.mode.value == "single":
            return [
                renderer.render_single(config.source_dir, config.output_dir, result)
                for result in results
            ]
        return [renderer.render_run(config.source_dir, config.output_dir, results)]

from pathlib import Path

from evidoc.application.located_result import LocatedResult
from evidoc.application.report_filename import safe_name
from evidoc.application.report_renderer import ReportRenderer
from evidoc.application.result_repository import ResultRepository
from evidoc.domain.evidoc_config import EvidocConfig
from evidoc.domain.report_format import ReportFormat
from evidoc.domain.status import Status


class GenerateReportUseCase:
    def __init__(
        self, result_repository: ResultRepository, renderers: dict[ReportFormat, ReportRenderer]
    ) -> None:
        self._result_repository = result_repository
        self._renderers = renderers

    def select(
        self, source_dir: Path, exclude_status: set[Status] | None = None
    ) -> list[LocatedResult]:
        return [
            item
            for item in self._result_repository.load_located_results(source_dir)
            if item.result.test_case.status not in (exclude_status or set())
        ]

    def execute(
        self, config: EvidocConfig, selected: list[LocatedResult] | None = None
    ) -> list[Path]:
        renderer = self._renderers[config.format]
        located = selected if selected is not None else self.select(config.source_dir)
        results = [item.result for item in located]
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
                renderer.render_single(item.source_dir, config.output_dir, item.result)
                for item in located
            ]
        sources = {item.result.test_id: item.source_dir for item in located}
        return [renderer.render_run(config.source_dir, config.output_dir, results, sources)]

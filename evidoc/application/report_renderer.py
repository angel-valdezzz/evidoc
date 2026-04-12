from pathlib import Path
from typing import Protocol

from evidoc.domain.run import Run


class ReportRenderer(Protocol):
    format_name: str

    def render_single(self, source_dir: Path, output_dir: Path, result: Run) -> Path: ...
    def render_run(self, source_dir: Path, output_dir: Path, results: list[Run]) -> Path: ...

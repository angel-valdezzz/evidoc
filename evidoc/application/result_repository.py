from pathlib import Path
from typing import Protocol

from evidoc.domain.run import Run


class ResultRepository(Protocol):
    def get_or_create_run_id(self, root_dir: Path) -> str: ...
    def save_test_result(self, root_dir: Path, result: Run) -> Path: ...
    def load_test_results(self, source_dir: Path) -> list[Run]: ...

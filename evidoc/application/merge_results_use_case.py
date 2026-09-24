from __future__ import annotations

from pathlib import Path

from evidoc.application.located_result import LocatedResult
from evidoc.application.result_repository import ResultRepository


class MergeResultsUseCase:
    def __init__(self, repository: ResultRepository) -> None:
        self._repository = repository

    def execute(self, input_dirs: list[Path], output_dir: Path) -> Path:
        if not input_dirs:
            raise ValueError("At least one metadata directory is required")
        selected: dict[str, LocatedResult] = {}
        for directory in input_dirs:
            if not directory.is_dir():
                raise ValueError(f"Metadata directory does not exist: {directory}")
            current: set[str] = set()
            for located in self._repository.load_located_results(directory):
                key = located.case_key
                if key in current:
                    raise ValueError(f"Duplicate case within metadata directory {directory}: {key}")
                current.add(key)
                selected[key] = located  # Later inputs replace the complete earlier attempt.
        if not selected:
            raise ValueError("No test results found in the metadata directories")
        return self._repository.save_merged_results(output_dir, list(selected.values()))

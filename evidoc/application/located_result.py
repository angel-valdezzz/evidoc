from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from evidoc.domain.run import Run


@dataclass(frozen=True, slots=True)
class LocatedResult:
    result: Run
    result_path: Path
    source_dir: Path

    @property
    def case_key(self) -> str:
        return self.result.test_case.full_name or self.result.test_case.name

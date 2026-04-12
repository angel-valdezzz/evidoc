from dataclasses import dataclass
from pathlib import Path

from evidoc.domain.run import Run


@dataclass(frozen=True, slots=True)
class RunManifest:
    run_id: str
    root_dir: Path
    tests: tuple[Run, ...] = ()

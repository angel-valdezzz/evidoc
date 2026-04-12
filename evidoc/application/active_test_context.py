from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from evidoc.domain.artifact import Artifact


@dataclass
class ActiveTestContext:
    root_dir: Path
    run_id: str
    test_id: str
    name: str
    application: str | None = None
    requirement: str | None = None
    steps: list[dict[str, Any]] = field(default_factory=list)
    artifacts: list[Artifact] = field(default_factory=list)

    @property
    def test_dir(self) -> Path:
        return self.root_dir / f"run-{self.run_id}" / f"test-{self.test_id}"

    @property
    def artifacts_dir(self) -> Path:
        return self.test_dir / "artifacts"

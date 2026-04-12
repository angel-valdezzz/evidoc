from pathlib import Path
from typing import Protocol

from evidoc.domain.artifact import Artifact
from evidoc.domain.artifact_type import ArtifactType


class ArtifactStorage(Protocol):
    def store_artifact(
        self,
        *,
        source_path: Path,
        artifacts_dir: Path,
        artifact_type: ArtifactType,
        title: str | None = None,
        description: str | None = None,
    ) -> Artifact | None: ...

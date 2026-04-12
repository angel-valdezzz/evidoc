from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from evidoc.application.artifact_storage import ArtifactStorage
from evidoc.domain.artifact import Artifact
from evidoc.domain.artifact_type import ArtifactType


class FilesystemArtifactStorage(ArtifactStorage):
    def store_artifact(
        self,
        *,
        source_path: Path,
        artifacts_dir: Path,
        artifact_type: ArtifactType,
        title: str | None = None,
        description: str | None = None,
    ) -> Artifact | None:
        if not source_path.exists():
            return None
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        if source_path.parent.resolve() == artifacts_dir.resolve():
            destination = source_path
            artifact_id = source_path.stem
        else:
            artifact_id = uuid4().hex
            destination = artifacts_dir / f"{artifact_id}{source_path.suffix or ''}"
            if source_path.resolve() != destination.resolve():
                shutil.copy2(source_path, destination)
        relative_path = destination.relative_to(artifacts_dir.parent).as_posix()
        return Artifact(
            id=artifact_id,
            type=artifact_type,
            path=relative_path,
            title=title,
            description=description,
        )

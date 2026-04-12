from dataclasses import dataclass

from evidoc.domain.artifact_type import ArtifactType


@dataclass(frozen=True, slots=True)
class Artifact:
    id: str
    type: ArtifactType
    path: str
    title: str | None = None
    description: str | None = None

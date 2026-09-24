from dataclasses import dataclass

from evidoc.domain.artifact_type import ArtifactType


@dataclass(frozen=True, slots=True)
class Artifact:
    id: str
    type: ArtifactType
    path: str | None = None
    title: str | None = None
    description: str | None = None
    data: str | None = None
    capture: str | None = None
    orientation: str | None = None
    external: bool = False

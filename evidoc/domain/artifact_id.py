from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ArtifactId:
    value: str

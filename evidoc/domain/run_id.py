from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RunId:
    value: str

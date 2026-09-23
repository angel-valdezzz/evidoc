from dataclasses import dataclass
from typing import ClassVar

from evidoc.domain.status import Status


@dataclass(frozen=True, slots=True)
class TestCase:
    __test__: ClassVar[bool] = False

    name: str
    status: Status
    duration: float
    application: str | None = None
    requirement: str | None = None
    project: str | None = None
    environment: str | None = None
    brand: str | None = None
    defect: str | None = None
    tags: tuple[str, ...] = ()

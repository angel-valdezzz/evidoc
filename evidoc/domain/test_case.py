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
    tags: tuple[str, ...] = ()

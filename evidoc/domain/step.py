from dataclasses import dataclass

from evidoc.domain.log_entry import LogEntry
from evidoc.domain.status import Status


@dataclass(frozen=True, slots=True)
class Step:
    title: str
    status: Status
    logs: tuple[LogEntry, ...] = ()
    artifact_ids: tuple[str, ...] = ()

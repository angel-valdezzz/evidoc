from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from evidoc.domain.status import Status


@dataclass(frozen=True, slots=True)
class LogEntry:
    level: Status
    message: str
    timestamp: str

    @classmethod
    def create(cls, level: Status, message: str) -> LogEntry:
        return cls(level=level, message=message, timestamp=datetime.now(UTC).isoformat())

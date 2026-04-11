from __future__ import annotations

from evidoc.domain.enums import Status


def status_color(status: Status) -> str:
    return {
        Status.PASS: "#2e7d32",
        Status.FAIL: "#b71c1c",
        Status.WARN: "#ed6c02",
        Status.INFO: "#1565c0",
        Status.SKIP: "#616161",
    }[status]

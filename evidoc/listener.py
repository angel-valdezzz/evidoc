from __future__ import annotations

"""Robot Framework listener that manages the Evidoc test lifecycle.

Use it with ``robot --listener evidoc.listener`` so every Robot test case opens
an Evidoc context at start and persists its evidence when execution finishes.
The listener is intentionally defensive: failures in evidence capture are
logged as warnings and should not break the Robot run by themselves.
"""

import logging
from contextvars import ContextVar
from time import perf_counter

from evidoc import api
from evidoc.domain.enums import Status

LOGGER = logging.getLogger("evidoc.listener")
ROBOT_LISTENER_API_VERSION = 3


class Listener:
    """Listener API v3 implementation used by Robot Framework."""

    def __init__(self) -> None:
        self._test_started_at: ContextVar[float | None] = ContextVar(
            "EVIDOC_LISTENER_TEST_STARTED_AT",
            default=None,
        )

    def start_test(self, data, result) -> None:
        try:
            api.start_test(getattr(data, "name", "Unnamed test"))
            self._test_started_at.set(perf_counter())
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("Unable to start Evidoc test context: %s", exc)

    def end_test(self, data, result) -> None:
        try:
            started_at = self._test_started_at.get()
            duration = 0.0 if started_at is None else perf_counter() - started_at
            api.end_test(self._map_status(getattr(result, "status", "INFO")), duration)
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("Unable to finish Evidoc test context: %s", exc)
        finally:
            api.clear_context()
            self._test_started_at.set(None)

    def close(self) -> None:
        api.clear_context()
        self._test_started_at.set(None)

    @staticmethod
    def _map_status(status: str) -> Status:
        normalized = status.upper()
        if normalized == "PASS":
            return Status.PASS
        if normalized == "FAIL":
            return Status.FAIL
        if normalized == "SKIP":
            return Status.SKIP
        return Status.INFO


_MODULE_LISTENER = Listener()


def start_test(data, result) -> None:
    _MODULE_LISTENER.start_test(data, result)


def end_test(data, result) -> None:
    _MODULE_LISTENER.end_test(data, result)


def close() -> None:
    _MODULE_LISTENER.close()

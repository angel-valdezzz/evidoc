from __future__ import annotations

import logging
from time import perf_counter

from evidoc.domain.enums import Status
from evidoc.infrastructure.bootstrap import build_runtime
from evidoc.infrastructure.robot.context import set_runtime


LOGGER = logging.getLogger("evidoc.listener")
ROBOT_LISTENER_API_VERSION = 3


class Listener:
    def __init__(self) -> None:
        self._runtime = build_runtime()
        self._test_started_at: float | None = None

    def start_test(self, data, result) -> None:
        try:
            self._runtime.start_test(data.name)
            set_runtime(self._runtime)
            self._test_started_at = perf_counter()
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("Unable to start Evidoc test context: %s", exc)

    def end_test(self, data, result) -> None:
        try:
            status = self._map_status(getattr(result, "status", "INFO"))
            duration = 0.0
            if self._test_started_at is not None:
                duration = perf_counter() - self._test_started_at
            self._runtime.finish_test(status, duration=duration)
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("Unable to finish Evidoc test context: %s", exc)
        finally:
            set_runtime(None)
            self._test_started_at = None

    def close(self) -> None:
        set_runtime(None)

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

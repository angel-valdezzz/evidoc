"""Robot Framework listener that manages the Evidoc test lifecycle.

Use it with ``robot --listener evidoc.listener`` so every Robot test case opens
an Evidoc context at start and persists its evidence when execution finishes.
The listener is intentionally defensive: failures in evidence capture are
logged as warnings and should not break the Robot run by themselves.
"""

from __future__ import annotations

import logging
from contextvars import ContextVar
from pathlib import Path
from time import perf_counter
from typing import Any

from robot.libraries.BuiltIn import BuiltIn

from evidoc import api
from evidoc.domain.enums import Status
from evidoc.infrastructure.config.repository import SchemaValidatedConfigRepository
from evidoc.schema_paths import config_schema_path

LOGGER = logging.getLogger("evidoc.listener")
ROBOT_LISTENER_API_VERSION = 3


class Listener:
    """Listener API v3 implementation used by Robot Framework."""

    def __init__(
        self,
        root_dir: str | None = None,
        storage: str | None = None,
        application: str | None = None,
        requirement: str | None = None,
        project: str | None = None,
        environment: str | None = None,
        brand: str | None = None,
        config_path: str | None = None,
    ) -> None:
        settings = SchemaValidatedConfigRepository(config_schema_path()).load(
            Path(config_path) if config_path else None
        )
        selected_storage = storage or settings.get("storage", "file")
        if selected_storage not in {"file", "base64"}:
            raise ValueError("storage must be 'file' or 'base64'")
        self.root_dir = root_dir or settings.get("metadata_dir")
        self.storage = selected_storage
        self.application = application or settings.get("application")
        self.requirement = requirement or settings.get("requirement")
        self.project = project or settings.get("project")
        self.environment = environment or settings.get("environment")
        self.brand = brand or settings.get("brand")
        self._test_started_at: ContextVar[float | None] = ContextVar(
            "EVIDOC_LISTENER_TEST_STARTED_AT",
            default=None,
        )

    def start_test(self, data: Any, result: Any) -> None:
        try:
            try:
                output_dir = BuiltIn().get_variable_value("${OUTPUT DIR}", ".")
            except Exception:  # RobotNotRunningError outside Robot execution
                output_dir = None
            if output_dir is not None or self.root_dir is not None:
                metadata = (
                    Path(self.root_dir)
                    if self.root_dir
                    else Path(output_dir) / "evidoc" / "metadata"
                )
                api.configure_context(
                    root_dir=metadata,
                    storage=self.storage,
                    application=self.application,
                    requirement=self.requirement,
                    project=self.project,
                    environment=self.environment,
                    brand=self.brand,
                )
            name = getattr(data, "name", "Unnamed test")
            full_name = getattr(data, "longname", None)
            if full_name is None:
                api.start_test(name)
            else:
                api.start_test(name, full_name=full_name)
            self._test_started_at.set(perf_counter())
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("Unable to start Evidoc test context: %s", exc)

    def end_test(self, data: Any, result: Any) -> None:
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


def start_test(data: Any, result: Any) -> None:
    _MODULE_LISTENER.start_test(data, result)


def end_test(data: Any, result: Any) -> None:
    _MODULE_LISTENER.end_test(data, result)


def close() -> None:
    _MODULE_LISTENER.close()

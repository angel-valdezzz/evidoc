from __future__ import annotations

import logging

from evidoc.application.ports import WarningSink


class LoggerWarningSink(WarningSink):
    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger("evidoc")

    def warn(self, message: str) -> None:
        self._logger.warning(message)

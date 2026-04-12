from __future__ import annotations

from pathlib import Path
from typing import Any

from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn

from evidoc import api

ROBOT_LIBRARY_SCOPE = "GLOBAL"
ROBOT_AUTO_KEYWORDS = False


@library(scope="GLOBAL", auto_keywords=False)
class RobotLibrary:
    @keyword("Log Step")
    def log_step(self, title: str, status: str = "INFO") -> None:
        api.log_step(title, status)

    @keyword("Capture Screenshot")
    def capture_screenshot(
        self,
        driver: Any | None = None,
        element: Any | None = None,
        title: str | None = None,
        description: str | None = None,
        library: str | None = None,
    ) -> str | None:
        target = driver
        if library:
            target = BuiltIn().get_library_instance(library)
        if target is None:
            raise ValueError("Capture Screenshot requires a driver or an explicit library name.")
        return api.capture_screenshot(target, element=element, title=title, description=description)

    @keyword("Attach Artifact")
    def attach_artifact(self, path: str | Path, description: str | None = None) -> str | None:
        return api.attach_artifact(path, description)

    @keyword("Log Info")
    def log_info(self, message: str) -> None:
        api.log_info(message)

    @keyword("Log Warning")
    def log_warning(self, message: str) -> None:
        api.log_warning(message)

    @keyword("Log Error")
    def log_error(self, message: str) -> None:
        api.log_error(message)


_LIBRARY = RobotLibrary()


@keyword("Log Step")
def log_step(title: str, status: str = "INFO") -> None:
    _LIBRARY.log_step(title, status)


@keyword("Capture Screenshot")
def capture_screenshot(
    driver: Any | None = None,
    element: Any | None = None,
    title: str | None = None,
    description: str | None = None,
    library: str | None = None,
) -> str | None:
    return _LIBRARY.capture_screenshot(
        driver=driver,
        element=element,
        title=title,
        description=description,
        library=library,
    )


@keyword("Attach Artifact")
def attach_artifact(path: str | Path, description: str | None = None) -> str | None:
    return _LIBRARY.attach_artifact(path, description)


@keyword("Log Info")
def log_info(message: str) -> None:
    _LIBRARY.log_info(message)


@keyword("Log Warning")
def log_warning(message: str) -> None:
    _LIBRARY.log_warning(message)


@keyword("Log Error")
def log_error(message: str) -> None:
    _LIBRARY.log_error(message)

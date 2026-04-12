from __future__ import annotations

"""Robot Framework library for capturing Evidoc execution evidence.

Import with ``Library    evidoc.robot`` when you want test steps, runtime logs,
screenshots, or support files to become part of the structured Evidoc result.

The library is intentionally thin: every keyword delegates to :mod:`evidoc.api`.
Use it together with ``--listener evidoc.listener`` so each Robot test opens and
closes its own Evidoc context automatically.
"""

from pathlib import Path
from typing import Any

from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn

from evidoc import api

ROBOT_LIBRARY_SCOPE = "GLOBAL"
ROBOT_AUTO_KEYWORDS = False


@library(scope="GLOBAL", auto_keywords=False)
class RobotLibrary:
    """Standard Robot Framework keyword library exposed by Evidoc.

    Recommended import:

    ``Library    evidoc.robot``

    Runtime expectation:

    ``robot --listener evidoc.listener ...``

    Keywords write evidence into the active test context managed by the
    listener. If no test context is active, the underlying API records a
    warning instead of failing silently.
    """

    @keyword("Log Step")
    def log_step(self, title: str, status: str = "INFO") -> None:
        """Create a business-readable step in the current test timeline.

        ``title`` is the visible step label in the generated evidence.
        ``status`` accepts Evidoc statuses such as ``PASS``, ``FAIL``,
        ``WARN`` or ``INFO``.
        """
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
        """Capture a screenshot from a driver or another Robot library.

        Pass ``driver`` when you already have a live browser or UI object.
        Pass ``library`` when the driver must be resolved through
        ``BuiltIn().get_library_instance(...)``, for example with
        ``SeleniumLibrary``.

        Returns the registered artifact id when the capture succeeds.
        """
        target = driver
        if library:
            target = BuiltIn().get_library_instance(library)
        if target is None:
            raise ValueError("Capture Screenshot requires a driver or an explicit library name.")
        return api.capture_screenshot(target, element=element, title=title, description=description)

    @keyword("Attach Artifact")
    def attach_artifact(self, path: str | Path, description: str | None = None) -> str | None:
        """Attach an existing local file to the active Evidoc test.

        ``path`` can be absolute or relative to the execution directory.
        ``description`` is optional supporting context shown in the report.
        Returns the stored artifact id when the file is accepted.
        """
        return api.attach_artifact(path, description)

    @keyword("Log Info")
    def log_info(self, message: str) -> None:
        """Append an informational runtime message to the current step."""
        api.log_info(message)

    @keyword("Log Warning")
    def log_warning(self, message: str) -> None:
        """Append a warning message to the current step."""
        api.log_warning(message)

    @keyword("Log Error")
    def log_error(self, message: str) -> None:
        """Append an error message to the current step."""
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

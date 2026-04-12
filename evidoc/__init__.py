"""Evidoc public package."""

from evidoc.api import (
    EvidocAPI,
    attach_artifact,
    attach_file,
    capture_screenshot,
    end_test,
    log_error,
    log_info,
    log_step,
    log_warning,
    start_test,
)

__all__ = [
    "__version__",
    "EvidocAPI",
    "attach_artifact",
    "attach_file",
    "capture_screenshot",
    "end_test",
    "log_error",
    "log_info",
    "log_step",
    "log_warning",
    "start_test",
]

__version__ = "0.1.0"

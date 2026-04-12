"""Evidoc public package."""

from evidoc.api import (
    EvidocAPI,
    attach_artifact,
    attach_file,
    clear_context,
    configure_context,
    capture_screenshot,
    end_test,
    get_current_api,
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
    "clear_context",
    "configure_context",
    "capture_screenshot",
    "end_test",
    "get_current_api",
    "log_error",
    "log_info",
    "log_step",
    "log_warning",
    "start_test",
]

__version__ = "0.1.0"

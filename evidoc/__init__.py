"""Evidoc public package."""

from evidoc.api import (
    EvidocAPI,
    attach_artifact,
    attach_file,
    build,
    capture_image,
    capture_screenshot,
    clear_context,
    configure_context,
    end_test,
    get_current_api,
    log_error,
    log_info,
    log_step,
    log_warning,
    merge,
    reference_file,
    set_defect,
    start_test,
)

__all__ = [
    "EvidocAPI",
    "__version__",
    "attach_artifact",
    "attach_file",
    "build",
    "capture_image",
    "capture_screenshot",
    "clear_context",
    "configure_context",
    "end_test",
    "get_current_api",
    "log_error",
    "log_info",
    "log_step",
    "log_warning",
    "merge",
    "reference_file",
    "set_defect",
    "start_test",
]

__version__ = "0.1.0"

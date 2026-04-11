from __future__ import annotations

from enum import StrEnum


class Status(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    INFO = "INFO"
    SKIP = "SKIP"


class ArtifactType(StrEnum):
    IMAGE = "image"
    FILE = "file"
    LOG = "log"


class ReportFormat(StrEnum):
    PDF = "pdf"
    DOCX = "docx"


class GenerateMode(StrEnum):
    SINGLE = "single"
    RUN = "run"

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from evidoc.domain.report_format import ReportFormat


@dataclass(frozen=True, slots=True)
class EvidocConfig:
    source_dir: Path = Path("./results")
    output_dir: Path = Path("./reports")
    format: ReportFormat = ReportFormat.PDF
    application: str | None = None
    requirement: str | None = None
    config_path: Path | None = None

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> EvidocConfig:
        source_dir = Path(payload.get("source_dir", "./results"))
        output_dir = Path(payload.get("output_dir", "./reports"))
        fmt = ReportFormat(payload.get("format", ReportFormat.PDF))
        config_path = payload.get("config_path")
        return cls(
            source_dir=source_dir,
            output_dir=output_dir,
            format=fmt,
            application=payload.get("application"),
            requirement=payload.get("requirement"),
            config_path=Path(config_path) if config_path else None,
        )

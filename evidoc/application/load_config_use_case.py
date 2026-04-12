from __future__ import annotations

from pathlib import Path
from typing import Any

from evidoc.application.config_repository import ConfigRepository
from evidoc.domain.evidoc_config import EvidocConfig


class LoadConfigUseCase:
    def __init__(self, config_repository: ConfigRepository) -> None:
        self._config_repository = config_repository

    def execute(self, config_path: Path | None = None, overrides: dict[str, Any] | None = None) -> EvidocConfig:
        payload = self._config_repository.load(config_path)
        merged = dict(payload)
        for key, value in (overrides or {}).items():
            if value is not None:
                merged[key] = value
        if config_path is not None:
            merged["config_path"] = str(config_path)
        return EvidocConfig.from_mapping(merged)

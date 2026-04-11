from __future__ import annotations

import json
import tomllib
from pathlib import Path

from jsonschema import validate

from evidoc.application.ports import ConfigRepository


class SchemaValidatedConfigRepository(ConfigRepository):
    def __init__(self, schema_path: Path) -> None:
        self._schema = json.loads(schema_path.read_text(encoding="utf-8"))

    def load(self, config_path: Path | None = None) -> dict:
        target = config_path or self._autodiscover()
        if target is None:
            return {}
        raw = self._load_file(target)
        validate(raw, self._schema)
        return raw

    def _autodiscover(self) -> Path | None:
        for name in ("evidoc.toml", "evidoc.json"):
            candidate = Path.cwd() / name
            if candidate.exists():
                return candidate
        return None

    def _load_file(self, path: Path) -> dict:
        if path.suffix.lower() == ".toml":
            return tomllib.loads(path.read_text(encoding="utf-8"))
        if path.suffix.lower() == ".json":
            return json.loads(path.read_text(encoding="utf-8"))
        raise ValueError(f"Unsupported config format: {path.suffix}")

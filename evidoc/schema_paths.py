"""Locations of schemas distributed with the EviDoc Python package."""

from pathlib import Path

_SCHEMAS = Path(__file__).resolve().parent / "resources" / "schemas"


def config_schema_path() -> Path:
    return _SCHEMAS / "config.schema.json"


def result_schema_path() -> Path:
    return _SCHEMAS / "result.schema.json"

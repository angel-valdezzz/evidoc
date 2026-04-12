from pathlib import Path
from typing import Protocol


class ConfigRepository(Protocol):
    def load(self, config_path: Path | None = None) -> dict: ...

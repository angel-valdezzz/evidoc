from typing import Protocol


class WarningSink(Protocol):
    def warn(self, message: str) -> None: ...

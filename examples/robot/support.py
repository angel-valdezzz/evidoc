from __future__ import annotations

from pathlib import Path

from robot.api.deco import keyword, library


class DemoDriver:
    def screenshot(self, path: str) -> bool:
        Path(path).write_bytes(b"png")
        return True


@library(scope="SUITE", auto_keywords=False)
class SupportLibrary:
    @keyword("Create Demo Artifact")
    def create_demo_artifact(self, path: str) -> str:
        artifact_path = Path(path)
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text("robot artifact", encoding="utf-8")
        return str(artifact_path)

    @keyword("Get Demo Driver")
    def get_demo_driver(self) -> DemoDriver:
        return DemoDriver()

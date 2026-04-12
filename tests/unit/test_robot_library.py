from __future__ import annotations

from pathlib import Path

import pytest

from evidoc.robot import RobotLibrary

pytestmark = pytest.mark.unit


def test_log_keywords_delegate_to_api(monkeypatch) -> None:
    calls: list[tuple[str, tuple]] = []
    library = RobotLibrary()

    monkeypatch.setattr("evidoc.robot.api.log_step", lambda title, status="INFO": calls.append(("step", (title, status))))
    monkeypatch.setattr("evidoc.robot.api.log_info", lambda message: calls.append(("info", (message,))))
    monkeypatch.setattr("evidoc.robot.api.log_warning", lambda message: calls.append(("warning", (message,))))
    monkeypatch.setattr("evidoc.robot.api.log_error", lambda message: calls.append(("error", (message,))))

    library.log_step("Open checkout", "PASS")
    library.log_info("hello")
    library.log_warning("watch out")
    library.log_error("broken")

    assert calls == [
        ("step", ("Open checkout", "PASS")),
        ("info", ("hello",)),
        ("warning", ("watch out",)),
        ("error", ("broken",)),
    ]


def test_attach_artifact_keyword_delegates_to_api(monkeypatch, tmp_path: Path) -> None:
    calls: list[tuple[Path, str | None]] = []
    library = RobotLibrary()
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("hello", encoding="utf-8")

    monkeypatch.setattr(
        "evidoc.robot.api.attach_artifact",
        lambda path, description=None: calls.append((Path(path), description)) or "artifact-id",
    )

    assert library.attach_artifact(artifact, "details") == "artifact-id"
    assert calls == [(artifact, "details")]


def test_capture_screenshot_keyword_uses_driver_instance(monkeypatch) -> None:
    calls: list[tuple[object, object, str | None, str | None]] = []
    library = RobotLibrary()
    driver = object()
    element = object()

    monkeypatch.setattr(
        "evidoc.robot.api.capture_screenshot",
        lambda driver, element=None, title=None, description=None: calls.append((driver, element, title, description))
        or "shot-id",
    )

    assert library.capture_screenshot(driver=driver, element=element, title="Dashboard", description="After login") == "shot-id"
    assert calls == [(driver, element, "Dashboard", "After login")]


def test_capture_screenshot_keyword_can_resolve_library(monkeypatch) -> None:
    calls: list[object] = []
    library = RobotLibrary()
    resolved_driver = object()

    monkeypatch.setattr("evidoc.robot.BuiltIn.get_library_instance", lambda self, name: resolved_driver)
    monkeypatch.setattr(
        "evidoc.robot.api.capture_screenshot",
        lambda driver, element=None, title=None, description=None: calls.append(driver) or "shot-id",
    )

    assert library.capture_screenshot(library="SeleniumLibrary") == "shot-id"
    assert calls == [resolved_driver]


def test_capture_screenshot_requires_explicit_target() -> None:
    with pytest.raises(ValueError):
        RobotLibrary().capture_screenshot()

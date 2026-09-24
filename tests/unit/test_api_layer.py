from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, cast

import pytest
from evidoc.api import (
    EvidocAPI,
    attach_artifact,
    clear_context,
    configure_context,
    end_test,
    get_current_api,
    log_info,
    log_step,
    start_test,
)
from evidoc.application.services import InMemoryWarningSink
from evidoc.domain.enums import Status
from evidoc.schema_paths import result_schema_path
from jsonschema import validate

pytestmark = pytest.mark.unit


def load_schema() -> dict[str, Any]:
    schema_path = result_schema_path()
    return cast(dict[str, Any], json.loads(schema_path.read_text(encoding="utf-8")))


def load_result(root_dir: Path, test_id: str) -> dict[str, Any]:
    run_id = (root_dir / ".run_id").read_text(encoding="utf-8").strip()
    result_path = root_dir / f"run-{run_id}" / f"test-{test_id}" / "result.json"
    return cast(dict[str, Any], json.loads(result_path.read_text(encoding="utf-8")))


def test_api_creates_run_test_and_artifact_structure(tmp_path: Path) -> None:
    api = EvidocAPI(root_dir=tmp_path / "results")
    attachment = tmp_path / "evidence.txt"
    attachment.write_text("artifact", encoding="utf-8")

    first_test_id = api.start_test("Checkout flow")
    api.log_step("Open checkout", "PASS")
    api.log_info("Navigated to checkout page")
    artifact_id = api.attach_file(attachment, "Input data")
    result_path = api.end_test("PASS", 1.25)

    second_test_id = api.start_test("Payment flow")
    api.end_test("FAIL", 0.5)

    assert first_test_id is not None
    assert second_test_id is not None
    assert first_test_id != second_test_id
    assert artifact_id is not None
    assert result_path is not None

    root_dir = tmp_path / "results"
    payload = load_result(root_dir, first_test_id)

    validate(payload, load_schema())
    assert payload["steps"][0]["artifact_ids"] == [artifact_id]
    assert payload["artifacts"][0]["path"].startswith("artifacts/")
    assert (root_dir / f"run-{payload['run_id']}" / f"test-{first_test_id}" / "artifacts").exists()


def test_attach_file_validates_existence_without_breaking(tmp_path: Path) -> None:
    api = EvidocAPI(root_dir=tmp_path / "results")

    api.start_test("Missing attachment")
    artifact_id = api.attach_file(tmp_path / "missing.txt", "not there")
    result_path = api.end_test("WARN", 0.1)

    assert artifact_id is None
    assert result_path is not None
    assert any("does not exist" in warning for warning in api.warnings)


def test_capture_screenshot_copies_image_into_artifacts(tmp_path: Path) -> None:
    api = EvidocAPI(root_dir=tmp_path / "results")

    class Driver:
        def screenshot(self, path: str) -> bool:
            Path(path).write_bytes(b"png")
            return True

    test_id = api.start_test("Screenshot flow")
    artifact_id = api.capture_screenshot(Driver(), title="Dashboard", description="After login")
    result_path = api.end_test("PASS", 0.2)

    assert test_id is not None
    assert artifact_id is not None
    assert result_path is not None

    run_id = (tmp_path / "results" / ".run_id").read_text(encoding="utf-8").strip()
    artifacts_dir = tmp_path / "results" / f"run-{run_id}" / f"test-{test_id}" / "artifacts"
    assert list(artifacts_dir.glob("*.png"))


def test_capture_screenshot_failure_never_breaks_execution(tmp_path: Path) -> None:
    api = EvidocAPI(root_dir=tmp_path / "results")

    class Driver:
        def save_screenshot(self, path: str) -> bool:
            return False

    api.start_test("Broken screenshot")
    artifact_id = api.capture_screenshot(Driver())
    result_path = api.end_test("INFO", 0.1)

    assert artifact_id is None
    assert result_path is not None
    assert any("Unable to capture screenshot" in warning for warning in api.warnings)


def test_log_methods_create_runtime_step_implicitly(tmp_path: Path) -> None:
    api = EvidocAPI(root_dir=tmp_path / "results")
    test_id = api.start_test("Implicit step logging")

    api.log_info("info message")
    api.log_warning("warn message")
    api.log_error("error message")
    api.end_test(Status.FAIL, 0.3)

    assert test_id is not None
    payload = load_result(tmp_path / "results", test_id)
    assert payload["steps"][0]["title"] == "Runtime messages"
    assert [entry["level"] for entry in payload["steps"][0]["logs"]] == ["INFO", "WARN", "FAIL"]


def test_end_test_without_active_context_returns_none(tmp_path: Path) -> None:
    api = EvidocAPI(root_dir=tmp_path / "results")

    result_path = api.end_test("PASS", 0.1)

    assert result_path is None
    assert any("No active test context to finish" in warning for warning in api.warnings)


def test_starting_new_test_closes_previous_one_safely(tmp_path: Path) -> None:
    api = EvidocAPI(root_dir=tmp_path / "results")

    first_test_id = api.start_test("Abandoned test")
    second_test_id = api.start_test("Replacement test")
    api.end_test("PASS", 0.2)

    assert first_test_id is not None
    assert second_test_id is not None
    assert first_test_id != second_test_id
    first_payload = load_result(tmp_path / "results", first_test_id)
    second_payload = load_result(tmp_path / "results", second_test_id)
    assert first_payload["test_case"]["status"] == "WARN"
    assert second_payload["test_case"]["status"] == "PASS"


def test_module_level_api_uses_configured_context(tmp_path: Path) -> None:
    configure_context(root_dir=tmp_path / "results")

    try:
        test_id = start_test("Robot wrapper flow")
        log_step("Keyword step", "PASS")
        log_info("Keyword info")
        result_path = end_test("PASS", 0.4)
    finally:
        clear_context()

    assert test_id is not None
    assert result_path is not None
    payload = load_result(tmp_path / "results", test_id)
    assert payload["test_case"]["name"] == "Robot wrapper flow"
    assert payload["steps"][0]["title"] == "Keyword step"
    assert payload["steps"][0]["logs"][0]["message"] == "Keyword info"


def test_module_level_api_isolated_per_thread(tmp_path: Path) -> None:
    results: list[tuple[str, str, int]] = []
    lock = threading.Lock()

    def worker(name: str) -> None:
        root_dir = tmp_path / name
        configure_context(root_dir=root_dir, warning_sink=InMemoryWarningSink())
        try:
            start_test(name)
            log_step(f"step-{name}", "PASS")
            artifact = root_dir / f"{name}.txt"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text(name, encoding="utf-8")
            attach_artifact(artifact, f"artifact-{name}")
            result_path = end_test("PASS", 0.1)
            with lock:
                results.append((name, str(result_path), id(get_current_api())))
        finally:
            clear_context()

    threads = [threading.Thread(target=worker, args=(name,)) for name in ("alpha", "beta")]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(results) == 2
    assert len({api_id for _, _, api_id in results}) == 2
    for name, result_path, _ in results:
        payload = json.loads(Path(result_path).read_text(encoding="utf-8"))
        assert payload["test_case"]["name"] == name
        assert payload["steps"][0]["title"] == f"step-{name}"

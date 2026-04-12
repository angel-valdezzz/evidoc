from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from evidoc.api import EvidocAPI
from evidoc.infrastructure.bootstrap import project_root


def load_schema() -> dict:
    schema_path = project_root() / "schemas" / "result.schema.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


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
    run_id = (root_dir / ".run_id").read_text(encoding="utf-8").strip()
    test_dir = root_dir / f"run-{run_id}" / f"test-{first_test_id}"
    payload = json.loads((test_dir / "result.json").read_text(encoding="utf-8"))

    validate(payload, load_schema())
    assert payload["run_id"] == run_id
    assert payload["test_id"] == first_test_id
    assert payload["steps"][0]["artifact_ids"] == [artifact_id]
    assert payload["artifacts"][0]["path"].startswith("artifacts/")
    assert (test_dir / "artifacts").exists()
    assert any((test_dir / "artifacts").iterdir())


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

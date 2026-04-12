from __future__ import annotations

import json
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from evidoc.api import EvidocAPI

pytestmark = pytest.mark.acceptance

scenarios("evidoc_api.feature")


@pytest.fixture
def context(tmp_path: Path) -> dict:
    return {
        "tmp_path": tmp_path,
        "results_dir": tmp_path / "results",
        "api": None,
        "attachment_path": None,
        "test_id": None,
        "result_path": None,
        "payload": None,
    }


@given("a clean Evidoc results directory")
def given_clean_results_directory(context: dict) -> None:
    context["api"] = EvidocAPI(root_dir=context["results_dir"])


@given(parsers.parse('an attachment file named "{filename}"'))
def given_attachment_file(context: dict, filename: str) -> None:
    attachment = context["tmp_path"] / filename
    attachment.write_text("acceptance artifact", encoding="utf-8")
    context["attachment_path"] = attachment


@when(parsers.parse('a test named "{test_name}" is captured through the Evidoc API'))
def when_start_test(context: dict, test_name: str) -> None:
    context["test_id"] = context["api"].start_test(test_name)


@when(parsers.parse('the step "{title}" is logged with status "{status}"'))
def when_log_step(context: dict, title: str, status: str) -> None:
    context["api"].log_step(title, status)


@when(parsers.parse('an info message "{message}" is logged'))
def when_log_info(context: dict, message: str) -> None:
    context["api"].log_info(message)


@when(parsers.parse('the attachment is added with description "{description}"'))
def when_attach_file(context: dict, description: str) -> None:
    context["api"].attach_file(context["attachment_path"], description)


@when("a missing attachment path is added")
def when_attach_missing_file(context: dict) -> None:
    context["api"].attach_file(context["tmp_path"] / "missing-artifact.txt", "missing")


@when(parsers.parse('the test ends with status "{status}" and duration {duration:f}'))
def when_end_test(context: dict, status: str, duration: float) -> None:
    context["result_path"] = context["api"].end_test(status, duration)
    if context["result_path"] is not None:
        context["payload"] = json.loads(Path(context["result_path"]).read_text(encoding="utf-8"))


@then("a result file is generated for the captured test")
def then_result_file_generated(context: dict) -> None:
    assert context["test_id"] is not None
    assert context["result_path"] is not None
    assert Path(context["result_path"]).exists()


@then(parsers.parse('the stored result declares status "{status}"'))
def then_result_status(context: dict, status: str) -> None:
    assert context["payload"]["test_case"]["status"] == status


@then("the stored result references one copied artifact")
def then_result_references_copied_artifact(context: dict) -> None:
    artifacts = context["payload"]["artifacts"]
    assert len(artifacts) == 1
    assert artifacts[0]["path"].startswith("artifacts/")
    artifact_path = Path(context["result_path"]).parent / Path(artifacts[0]["path"])
    assert artifact_path.exists()


@then("the warning log mentions a missing artifact")
def then_warning_mentions_missing_artifact(context: dict) -> None:
    assert any("does not exist" in message for message in context["api"].warnings)

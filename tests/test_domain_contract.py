from __future__ import annotations

import json
from pathlib import Path

import pytest

from evidoc.domain import SCHEMA_VERSION, run_from_dict, validate_run_payload
from evidoc.domain.enums import ArtifactType, Status
from evidoc.domain.models import Artifact, LogEntry, Run, Step, TestCase


def load_example_payload() -> dict:
    example_path = Path(__file__).resolve().parents[1] / "examples" / "run-result.example.json"
    return json.loads(example_path.read_text(encoding="utf-8"))


def test_example_payload_matches_schema_and_reference_rules() -> None:
    payload = load_example_payload()
    validate_run_payload(payload)
    run = run_from_dict(payload)
    assert run.schema_version == SCHEMA_VERSION
    assert run.steps[1].artifact_ids == ("art_dashboard", "art_network_log")


def test_run_rejects_dangling_artifact_reference() -> None:
    with pytest.raises(ValueError, match="globally declared artifact"):
        Run(
            schema_version=SCHEMA_VERSION,
            run_id="run_001",
            test_id="test_001",
            generated_at="2026-04-11T23:03:17Z",
            test_case=TestCase(name="Example", status=Status.FAIL, duration=1.5),
            steps=(
                Step(
                    title="Missing evidence",
                    status=Status.FAIL,
                    logs=(LogEntry(level=Status.INFO, message="No screenshot saved", timestamp="2026-04-11T23:03:17Z"),),
                    artifact_ids=("missing_artifact",),
                ),
            ),
            artifacts=(),
        )


def test_payload_rejects_duplicate_artifact_ids() -> None:
    payload = load_example_payload()
    payload["artifacts"].append(
        {
            "id": "art_dashboard",
            "type": "file",
            "path": "artifacts/duplicate.txt",
            "title": "Duplicate",
            "description": None,
        }
    )

    with pytest.raises(ValueError, match="Duplicate artifact IDs"):
        validate_run_payload(payload)


def test_run_serializes_artifacts_separately_from_steps() -> None:
    run = Run(
        schema_version=SCHEMA_VERSION,
        run_id="run_001",
        test_id="test_001",
        generated_at="2026-04-11T23:03:17Z",
        test_case=TestCase(
            name="Checkout flow",
            status=Status.PASS,
            duration=3.2,
            application="Evidence Portal",
            requirement="CHK-010",
            tags=("smoke",),
        ),
        steps=(
            Step(
                title="Capture invoice",
                status=Status.PASS,
                logs=(),
                artifact_ids=("invoice_pdf",),
            ),
        ),
        artifacts=(
            Artifact(
                id="invoice_pdf",
                type=ArtifactType.FILE,
                path="artifacts/invoice.pdf",
                title="Generated invoice",
                description=None,
            ),
        ),
    )

    payload = run.to_dict()

    assert payload["steps"][0]["artifact_ids"] == ["invoice_pdf"]
    assert "artifacts" not in payload["steps"][0]
    assert payload["artifacts"][0]["id"] == "invoice_pdf"

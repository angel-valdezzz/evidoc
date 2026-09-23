from __future__ import annotations

import base64
import re
from pathlib import Path

from evidoc.domain.artifact import Artifact
from evidoc.domain.enums import Status
from evidoc.domain.run import Run


def status_color(status: Status) -> str:
    return {
        Status.PASS: "#2e7d32",
        Status.FAIL: "#b71c1c",
        Status.WARN: "#ed6c02",
        Status.INFO: "#1565c0",
        Status.SKIP: "#616161",
    }[status]


def summary_rows(result: Run) -> list[tuple[str, str]]:
    case = result.test_case
    return [
        ("Aplicación", case.application or "—"),
        ("Requerimiento", case.requirement or "—"),
        ("Caso de Prueba", case.name),
        ("Estatus", case.status.value),
        ("Duración", f"{case.duration:.2f} s"),
    ]


def image_bytes(source_dir: Path, result: Run, artifact: Artifact) -> bytes | None:
    if artifact.data is not None:
        return base64.b64decode(artifact.data, validate=True)
    if artifact.path is None:
        return None
    test_dir = (source_dir / f"run-{result.run_id}" / f"test-{result.test_id}").resolve()
    image = (test_dir / artifact.path).resolve()
    if not image.is_relative_to(test_dir):
        raise ValueError("Artifact path escapes the test directory")
    return image.read_bytes() if image.is_file() else None


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._") or "test"

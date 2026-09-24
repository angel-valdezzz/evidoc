"""A small, machine-readable list of files for downstream upload tools."""

from __future__ import annotations

import json
from pathlib import Path

from evidoc.application.located_result import LocatedResult
from evidoc.application.report_filename import safe_name
from evidoc.domain.artifact_type import ArtifactType


def external_files(results: list[LocatedResult]) -> None:
    """Reject broken references before generating any reports or upload instructions."""
    for item in results:
        for artifact in item.result.artifacts:
            if (
                artifact.type == ArtifactType.FILE
                and artifact.external
                and (not artifact.path or not Path(artifact.path).is_file())
            ):
                raise FileNotFoundError(
                    f"Attached file is missing for {item.result.test_case.name}: {artifact.path}"
                )


def write_upload_manifest(
    output_dir: Path,
    results: list[LocatedResult],
    reports: list[Path],
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    cases: list[dict[str, object]] = []
    for item in results:
        stem = safe_name(item.result.test_case.name)
        files = [path.resolve() for path in reports if path.stem == stem]
        files += [
            Path(artifact.path).resolve()
            for artifact in item.result.artifacts
            if artifact.type == ArtifactType.FILE and artifact.external and artifact.path
        ]
        cases.append({"name": item.result.test_case.name, "files": [str(path) for path in files]})
    path = output_dir / "upload-manifest.json"
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps({"tests": cases}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    temporary.replace(path)
    return path

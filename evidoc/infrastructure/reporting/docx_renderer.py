from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.shared import Inches

from evidoc.application.ports import ReportRenderer
from evidoc.domain.enums import ArtifactType
from evidoc.domain.models import TestResult


class DocxReportRenderer(ReportRenderer):
    format_name = "docx"

    def render_single(self, source_dir: Path, output_dir: Path, result: TestResult) -> Path:
        output = output_dir / f"{result.test_case.name.replace(' ', '_')}-{result.test_id}.docx"
        self._build(output, source_dir, [result])
        return output

    def render_run(self, source_dir: Path, output_dir: Path, results: list[TestResult]) -> Path:
        run_id = results[0].run_id if results else "empty"
        output = output_dir / f"run-{run_id}.docx"
        self._build(output, source_dir, results)
        return output

    def _build(self, output_path: Path, source_dir: Path, results: list[TestResult]) -> None:
        document = Document()
        document.add_heading("Evidoc Report", level=0)
        for index, result in enumerate(results):
            if index:
                document.add_page_break()
            document.add_heading(result.test_case.name, level=1)
            document.add_paragraph(f"Status: {result.test_case.status}")
            document.add_paragraph(f"Duration: {result.test_case.duration:.2f}s")
            if result.test_case.application:
                document.add_paragraph(f"Application: {result.test_case.application}")
            if result.test_case.requirement:
                document.add_paragraph(f"Requirement: {result.test_case.requirement}")
            artifact_map = {artifact.id: artifact for artifact in result.artifacts}
            image_count = 0
            for step in result.steps:
                document.add_heading(step.title, level=2)
                document.add_paragraph(f"Status: {step.status}")
                for log in step.logs:
                    document.add_paragraph(f"[{log.level}] {log.message}")
                for artifact_id in step.artifact_ids:
                    artifact = artifact_map.get(artifact_id)
                    if artifact is None:
                        continue
                    if artifact.type == ArtifactType.IMAGE:
                        image_path = source_dir / f"run-{result.run_id}" / f"test-{result.test_id}" / artifact.path
                        document.add_paragraph(artifact.title or "Screenshot")
                        if artifact.description:
                            document.add_paragraph(artifact.description)
                        if image_path.exists():
                            document.add_picture(str(image_path), width=Inches(4.8))
                        image_count += 1
                        if image_count % 2 == 0:
                            document.add_page_break()
                    else:
                        document.add_paragraph(f"Attachment: {artifact.title or artifact.path}")
        document.save(str(output_path))

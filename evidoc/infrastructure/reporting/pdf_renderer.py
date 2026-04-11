from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from evidoc.application.ports import ReportRenderer
from evidoc.domain.enums import ArtifactType, Status
from evidoc.domain.models import ArtifactRef, TestResult
from evidoc.infrastructure.reporting.helpers import status_color


class PdfReportRenderer(ReportRenderer):
    format_name = "pdf"

    def render_single(self, source_dir: Path, output_dir: Path, result: TestResult) -> Path:
        output = output_dir / f"{result.test_case.name.replace(' ', '_')}-{result.test_id}.pdf"
        self._build(output, source_dir, [result])
        return output

    def render_run(self, source_dir: Path, output_dir: Path, results: list[TestResult]) -> Path:
        run_id = results[0].run_id if results else "empty"
        output = output_dir / f"run-{run_id}.pdf"
        self._build(output, source_dir, results)
        return output

    def _build(self, output_path: Path, source_dir: Path, results: list[TestResult]) -> None:
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(str(output_path), pagesize=A4, title="Evidoc Report")
        story = [Paragraph("Evidoc Report", styles["Title"]), Spacer(1, 0.2 * inch)]
        for index, result in enumerate(results):
            story.extend(self._test_section(result, styles, source_dir))
            if index < len(results) - 1:
                story.append(PageBreak())
        doc.build(story)

    def _test_section(self, result: TestResult, styles, source_dir: Path) -> list:
        items = [
            Paragraph(result.test_case.name, styles["Heading1"]),
            Paragraph(f"Status: <font color='{status_color(result.test_case.status)}'>{result.test_case.status}</font>", styles["Normal"]),
            Paragraph(f"Duration: {result.test_case.duration:.2f}s", styles["Normal"]),
        ]
        if result.test_case.application:
            items.append(Paragraph(f"Application: {result.test_case.application}", styles["Normal"]))
        if result.test_case.requirement:
            items.append(Paragraph(f"Requirement: {result.test_case.requirement}", styles["Normal"]))
        items.append(Spacer(1, 0.15 * inch))
        artifact_map = {artifact.id: artifact for artifact in result.artifacts}
        screenshot_count = 0
        for step in result.steps:
            data = [[Paragraph(f"<b>{step.title}</b>", styles["BodyText"]), Paragraph(str(step.status), styles["BodyText"])]]
            table = Table(data, colWidths=[4.8 * inch, 1.2 * inch])
            bg = colors.HexColor("#fdecea" if step.status == Status.FAIL else "#f7f9fc")
            table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey)]))
            items.extend([table, Spacer(1, 0.08 * inch)])
            for log in step.logs:
                items.append(Paragraph(f"[{log.level}] {log.message}", styles["BodyText"]))
            for artifact_id in step.artifact_ids:
                artifact = artifact_map.get(artifact_id)
                if artifact is None:
                    continue
                if artifact.type == ArtifactType.IMAGE:
                    if screenshot_count and screenshot_count % 2 == 0:
                        items.append(PageBreak())
                    items.extend(self._image_block(result, artifact, source_dir, styles))
                    screenshot_count += 1
                else:
                    items.append(Paragraph(f"Attachment: {artifact.title or artifact.path}", styles["BodyText"]))
            items.append(Spacer(1, 0.15 * inch))
        return items

    def _image_block(self, result: TestResult, artifact: ArtifactRef, source_dir: Path, styles) -> list:
        image_path = source_dir / f"run-{result.run_id}" / f"test-{result.test_id}" / artifact.path
        if not image_path.exists():
            return [Paragraph(f"Missing image: {artifact.path}", styles["BodyText"])]
        block = [Paragraph(artifact.title or "Screenshot", styles["Heading3"])]
        if artifact.description:
            block.append(Paragraph(artifact.description, styles["BodyText"]))
        block.append(Image(str(image_path), width=3.0 * inch, height=2.2 * inch))
        block.append(Spacer(1, 0.1 * inch))
        return block

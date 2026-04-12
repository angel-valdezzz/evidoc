from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import HRFlowable, Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from evidoc.application.ports import ReportRenderer
from evidoc.domain.enums import ArtifactType, Status
from evidoc.domain.models import ArtifactRef, TestResult
from evidoc.infrastructure.reporting.helpers import status_color


class PdfReportRenderer(ReportRenderer):
    format_name = "pdf"

    def render_single(self, source_dir: Path, output_dir: Path, result: TestResult) -> Path:
        output = output_dir / f"{self._safe_name(result.test_case.name)}-{result.test_id}.pdf"
        self._build(output, source_dir, [result])
        return output

    def render_run(self, source_dir: Path, output_dir: Path, results: list[TestResult]) -> Path:
        run_ids = {result.run_id for result in results}
        run_id = results[0].run_id if len(run_ids) == 1 and results else "combined"
        output = output_dir / f"run-{run_id}.pdf"
        self._build(output, source_dir, results)
        return output

    def _build(self, output_path: Path, source_dir: Path, results: list[TestResult]) -> None:
        styles = self._styles()
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            title="Evidoc Report",
            leftMargin=0.65 * inch,
            rightMargin=0.65 * inch,
            topMargin=0.7 * inch,
            bottomMargin=0.65 * inch,
        )
        story = [Paragraph("Evidoc Report", styles["Title"]), Spacer(1, 0.14 * inch)]
        for index, result in enumerate(results):
            story.extend(self._test_section(result, styles, source_dir))
            if index < len(results) - 1:
                story.append(PageBreak())
        doc.build(story)

    def _styles(self) -> dict[str, ParagraphStyle]:
        styles = getSampleStyleSheet()
        styles["Title"].fontSize = 22
        styles["Title"].leading = 28
        styles["Heading1"].fontSize = 16
        styles["Heading1"].leading = 20
        styles["Heading2"].fontSize = 11
        styles["Heading2"].leading = 14
        styles["BodyText"].fontSize = 9
        styles["BodyText"].leading = 12
        styles.add(
            ParagraphStyle(
                name="Meta",
                parent=styles["BodyText"],
                textColor=colors.HexColor("#344054"),
                spaceAfter=2,
            )
        )
        styles.add(
            ParagraphStyle(
                name="Muted",
                parent=styles["BodyText"],
                textColor=colors.HexColor("#667085"),
                spaceAfter=6,
            )
        )
        styles.add(
            ParagraphStyle(
                name="StatusBadge",
                parent=styles["BodyText"],
                fontSize=8,
                leading=10,
                alignment=TA_CENTER,
                textColor=colors.white,
            )
        )
        return styles

    def _test_section(self, result: TestResult, styles: dict[str, ParagraphStyle], source_dir: Path) -> list:
        items: list = [
            Paragraph(result.test_case.name, styles["Heading1"]),
            Spacer(1, 0.04 * inch),
            self._status_badge(result.test_case.status.value, styles),
            Spacer(1, 0.10 * inch),
        ]

        for label, value in self._metadata_rows(result):
            items.append(Paragraph(f"<b>{label}:</b> {value}", styles["Meta"]))

        items.extend([Spacer(1, 0.08 * inch), self._separator(), Spacer(1, 0.08 * inch)])
        items.append(Paragraph("Steps", styles["Heading2"]))
        items.append(Spacer(1, 0.04 * inch))

        artifact_map = {artifact.id: artifact for artifact in result.artifacts}
        image_refs: list[tuple[str, ArtifactRef]] = []

        for step_index, step in enumerate(result.steps, start=1):
            items.extend(self._step_block(step_index, step.title, step.status.value, styles))

            if step.logs:
                for log in step.logs:
                    items.append(
                        Paragraph(
                            f"[{log.level.value}] {self._escape(log.message)}",
                            styles["BodyText"],
                        )
                    )
            else:
                items.append(Paragraph("No logs recorded.", styles["Muted"]))

            attachments = [artifact_map[artifact_id] for artifact_id in step.artifact_ids if artifact_id in artifact_map]
            file_refs = [artifact for artifact in attachments if artifact.type != ArtifactType.IMAGE]
            for artifact in file_refs:
                label = artifact.title or artifact.path
                items.append(Paragraph(f"Attachment: {self._escape(label)}", styles["Muted"]))

            for artifact in attachments:
                if artifact.type == ArtifactType.IMAGE:
                    image_refs.append((step.title, artifact))

            if step_index < len(result.steps):
                items.extend([Spacer(1, 0.06 * inch), self._separator(light=True), Spacer(1, 0.06 * inch)])

        if image_refs:
            items.append(PageBreak())
            items.append(Paragraph("Image Evidence", styles["Heading2"]))
            items.append(Spacer(1, 0.06 * inch))
            for index, (step_title, artifact) in enumerate(image_refs):
                if index and index % 2 == 0:
                    items.append(PageBreak())
                items.extend(self._image_block(result, step_title, artifact, source_dir, styles))

        return items

    def _metadata_rows(self, result: TestResult) -> list[tuple[str, str]]:
        rows = [
            ("Test ID", result.test_id),
            ("Run ID", result.run_id),
            ("Generated", result.generated_at),
            ("Duration", f"{result.test_case.duration:.2f}s"),
        ]
        if result.test_case.application:
            rows.append(("Application", result.test_case.application))
        if result.test_case.requirement:
            rows.append(("Requirement", result.test_case.requirement))
        return rows

    def _step_block(self, step_number: int, title: str, status: str, styles: dict[str, ParagraphStyle]) -> list:
        table = Table(
            [[Paragraph(f"<b>{step_number}. {self._escape(title)}</b>", styles["BodyText"]), self._status_badge(status, styles)]],
            colWidths=[5.55 * inch, 0.95 * inch],
        )
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#d0d5dd")),
                    ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#f8fafc")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        return [table, Spacer(1, 0.05 * inch)]

    def _image_block(
        self,
        result: TestResult,
        step_title: str,
        artifact: ArtifactRef,
        source_dir: Path,
        styles: dict[str, ParagraphStyle],
    ) -> list:
        image_path = source_dir / f"run-{result.run_id}" / f"test-{result.test_id}" / Path(artifact.path)
        block = [
            Paragraph(f"<b>Step:</b> {self._escape(step_title)}", styles["BodyText"]),
            Paragraph(self._escape(artifact.title or "Screenshot"), styles["BodyText"]),
        ]
        if artifact.description:
            block.append(Paragraph(self._escape(artifact.description), styles["Muted"]))
        else:
            block.append(Spacer(1, 0.03 * inch))

        if not image_path.exists():
            block.extend(
                [
                    Paragraph(f"Missing image: {self._escape(artifact.path)}", styles["Muted"]),
                    Spacer(1, 0.12 * inch),
                ]
            )
            return block

        width, height = self._scaled_image_size(image_path, max_width=6.2 * inch, max_height=3.2 * inch)
        block.extend(
            [
                Image(str(image_path), width=width, height=height),
                Spacer(1, 0.12 * inch),
            ]
        )
        return block

    def _scaled_image_size(self, image_path: Path, *, max_width: float, max_height: float) -> tuple[float, float]:
        raw_width, raw_height = ImageReader(str(image_path)).getSize()
        if not raw_width or not raw_height:
            return max_width, max_height
        scale = min(max_width / raw_width, max_height / raw_height, 1.0)
        return raw_width * scale, raw_height * scale

    def _separator(self, *, light: bool = False) -> HRFlowable:
        return HRFlowable(
            width="100%",
            thickness=0.6 if light else 0.8,
            color=colors.HexColor("#d0d5dd" if light else "#98a2b3"),
            spaceBefore=0,
            spaceAfter=0,
        )

    def _status_badge(self, status: str, styles: dict[str, ParagraphStyle]) -> Table:
        normalized = Status(status)
        table = Table([[Paragraph(status, styles["StatusBadge"])]], colWidths=[0.88 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(status_color(normalized))),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return table

    def _safe_name(self, value: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._") or "test"

    def _escape(self, value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

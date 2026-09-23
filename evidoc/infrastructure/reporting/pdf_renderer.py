"""Business evidence PDF built from the renderer-neutral result model."""

from __future__ import annotations

from html import escape
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from evidoc.application.report_renderer import ReportRenderer
from evidoc.domain.artifact_type import ArtifactType
from evidoc.domain.run import Run
from evidoc.infrastructure.reporting.helpers import (
    image_bytes,
    safe_name,
    status_color,
    summary_rows,
)

NAVY = colors.HexColor("#2c3e50")
PALE = colors.HexColor("#f8f9fa")
BORDER = colors.HexColor("#dee2e6")


class PdfReportRenderer(ReportRenderer):
    format_name = "pdf"

    def render_single(self, source_dir: Path, output_dir: Path, result: Run) -> Path:
        output = output_dir / f"{safe_name(result.test_case.name)}-{result.test_id}.pdf"
        self._build(output, source_dir, [result])
        return output

    def render_run(self, source_dir: Path, output_dir: Path, results: list[Run]) -> Path:
        run_ids = {result.run_id for result in results}
        run_id = results[0].run_id if len(run_ids) == 1 else "combined"
        output = output_dir / f"run-{run_id}.pdf"
        self._build(output, source_dir, results)
        return output

    def _build(self, output: Path, source_dir: Path, results: list[Run]) -> None:
        styles = getSampleStyleSheet()
        styles["Title"].textColor = NAVY
        styles["Title"].fontSize = 19
        styles["Heading2"].textColor = NAVY
        styles["BodyText"].leading = 13
        story: list = []
        for index, result in enumerate(results):
            if index:
                story.append(PageBreak())
            story += [
                Paragraph("Reporte de Ejecución Automatizada", styles["Title"]),
                Spacer(1, 0.4 * cm),
                Paragraph("Resumen De Ejecución", styles["Heading2"]),
                Spacer(1, 0.15 * cm),
            ]
            rows = [[label, value] for label, value in summary_rows(result)]
            table = Table(rows, colWidths=[3.5 * cm, 13.5 * cm], hAlign="LEFT")
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, -1), NAVY),
                        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
                        ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.white, PALE]),
                        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ]
                )
            )
            story += [table, Spacer(1, 0.6 * cm)]
            artifacts = {artifact.id: artifact for artifact in result.artifacts}
            image_count = 0
            for step in result.steps:
                starts_new_page = (
                    image_count > 0
                    and image_count % 2 == 0
                    and any(
                        artifacts[identifier].type == ArtifactType.IMAGE
                        for identifier in step.artifact_ids
                    )
                )
                if starts_new_page:
                    story.append(PageBreak())
                story.append(Paragraph(escape(step.title), styles["Heading2"]))
                story.append(
                    Paragraph(
                        f'<font color="{status_color(step.status)}">{step.status.value}</font>',
                        styles["BodyText"],
                    )
                )
                for log in step.logs:
                    story.append(Paragraph(escape(log.message), styles["BodyText"]))
                for identifier in step.artifact_ids:
                    artifact = artifacts[identifier]
                    if artifact.type != ArtifactType.IMAGE:
                        story.append(
                            Paragraph(
                                "Adjunto: " + escape(artifact.title or artifact.path or identifier),
                                styles["BodyText"],
                            )
                        )
                        continue
                    if image_count and image_count % 2 == 0 and not starts_new_page:
                        story.append(PageBreak())
                    image_count += 1
                    starts_new_page = False
                    block: list = [
                        Paragraph(escape(artifact.title or "Evidencia"), styles["BodyText"])
                    ]
                    if artifact.description:
                        block.append(Paragraph(escape(artifact.description), styles["BodyText"]))
                    data = image_bytes(source_dir, result, artifact)
                    if data:
                        reader = ImageReader(BytesIO(data))
                        width, height = reader.getSize()
                        max_height = 16 * cm if artifact.orientation == "vertical" else 12 * cm
                        ratio = min(17 * cm / width, max_height / height, 1)
                        block.append(
                            Image(BytesIO(data), width=width * ratio, height=height * ratio)
                        )
                    else:
                        block.append(Paragraph("Imagen no disponible", styles["BodyText"]))
                    block.append(Spacer(1, 0.35 * cm))
                    story.append(KeepTogether(block))
                story.append(Spacer(1, 0.25 * cm))
        doc = SimpleDocTemplate(
            str(output),
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
            title="Reporte de Ejecución Automatizada",
        )
        doc.build(story, onFirstPage=self._header, onLaterPages=self._header)

    @staticmethod
    def _header(canvas: Any, doc: Any) -> None:
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, A4[1] - 1 * cm, A4[0], 1 * cm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(2 * cm, A4[1] - 0.65 * cm, "EviDoc")
        canvas.setFillColor(NAVY)
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(A4[0] - 2 * cm, 0.9 * cm, f"{doc.page}")
        canvas.restoreState()

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

from evidoc.application.report_filename import safe_name
from evidoc.application.report_renderer import ReportRenderer
from evidoc.domain.artifact_type import ArtifactType
from evidoc.domain.run import Run
from evidoc.infrastructure.reporting.helpers import (
    fitted_size,
    image_bytes,
    report_date,
    status_color,
    summary_rows,
)

BLUE = colors.HexColor("#2f50c5")
RED = colors.HexColor("#c62828")
NAVY = colors.HexColor("#242a35")
PALE = colors.HexColor("#f8f9fa")
BORDER = colors.HexColor("#dee2e6")


class PdfReportRenderer(ReportRenderer):
    format_name = "pdf"

    def render_single(self, source_dir: Path, output_dir: Path, result: Run) -> Path:
        output = output_dir / f"{safe_name(result.test_case.name)}.pdf"
        self._build(output, source_dir, [result])
        return output

    def render_run(
        self,
        source_dir: Path,
        output_dir: Path,
        results: list[Run],
        sources: dict[str, Path] | None = None,
    ) -> Path:
        run_ids = {result.run_id for result in results}
        run_id = results[0].run_id if len(run_ids) == 1 else "combined"
        output = output_dir / f"run-{run_id}.pdf"
        self._build(output, source_dir, results, sources)
        return output

    def _build(
        self,
        output: Path,
        source_dir: Path,
        results: list[Run],
        sources: dict[str, Path] | None = None,
    ) -> None:
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
                Paragraph(
                    f'<para align="right">Fecha: {report_date(result)}</para>',
                    styles["BodyText"],
                ),
                Spacer(1, 0.3 * cm),
                Paragraph("Reporte de Ejecución Automatizada", styles["Title"]),
                Spacer(1, 0.9 * cm),
                Paragraph("Resumen De Ejecución", styles["Heading2"]),
                Spacer(1, 0.5 * cm),
            ]
            rows = [[label, value] for label, value in summary_rows(result)]
            table = Table(rows, colWidths=[8.2 * cm, 8.8 * cm], hAlign="LEFT")
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, -2), BLUE),
                        ("BACKGROUND", (0, -1), (0, -1), RED),
                        ("BACKGROUND", (1, -1), (1, -1), colors.HexColor("#fff5f5")),
                        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
                        ("ROWBACKGROUNDS", (1, 0), (1, -2), [colors.white, PALE]),
                        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ]
                )
            )
            story.append(table)
            if result.steps:
                story.append(PageBreak())
            artifacts = {artifact.id: artifact for artifact in result.artifacts}
            image_count = 0
            for step in result.steps:
                color = status_color(step.status)
                heading = Paragraph(
                    f'<font color="{color}">&#9830;</font> {escape(step.title)} '
                    f'<font color="{color}">&#9830;</font>',
                    styles["Heading2"],
                )
                has_image = any(
                    artifacts[identifier].type == ArtifactType.IMAGE
                    for identifier in step.artifact_ids
                )
                if not has_image:
                    story.append(heading)
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
                    if image_count == 2:
                        story.append(PageBreak())
                        image_count = 0
                    image_count += 1
                    block: list = [heading]
                    if artifact.title and artifact.title != step.title:
                        block.append(Paragraph(escape(artifact.title), styles["BodyText"]))
                    data = image_bytes(
                        (sources or {}).get(result.test_id, source_dir), result, artifact
                    )
                    if data:
                        reader = ImageReader(BytesIO(data))
                        width, height = reader.getSize()
                        max_height = 16 * cm if artifact.orientation == "vertical" else 9 * cm
                        display_width, display_height = fitted_size(
                            width, height, 17 * cm, max_height
                        )
                        block.append(
                            Image(BytesIO(data), width=display_width, height=display_height)
                        )
                    else:
                        block.append(Paragraph("Imagen no disponible", styles["BodyText"]))
                    if artifact.description:
                        block.append(Paragraph(escape(artifact.description), styles["BodyText"]))
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

        def header(canvas: Any, document: Any) -> None:
            self._header(canvas, document, results[0])

        doc.build(story, onFirstPage=header, onLaterPages=header)

    @staticmethod
    def _header(canvas: Any, doc: Any, result: Run) -> None:
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(2 * cm, A4[1] - 1.15 * cm, result.test_case.brand or "EviDoc")
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.15 * cm, result.test_case.project or "")
        canvas.setFont("Helvetica", 8)
        canvas.drawString(2 * cm, 0.9 * cm, f"Ambiente: {result.test_case.environment or '—'}")
        canvas.drawRightString(A4[0] - 2 * cm, 0.9 * cm, f"Página {doc.page}")
        canvas.restoreState()

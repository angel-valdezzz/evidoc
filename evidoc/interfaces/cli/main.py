from __future__ import annotations

from pathlib import Path

import typer

from evidoc import build
from evidoc.documentation import available_documents, open_documentation
from evidoc.domain.generate_mode import GenerateMode
from evidoc.domain.report_format import ReportFormat
from evidoc.infrastructure.bootstrap import build_generate_use_case
from evidoc.interfaces.tui.app import EvidocTui

app = typer.Typer(help="Evidoc reporting CLI.")
docs_app = typer.Typer(help="Open bundled Evidoc documentation.")
app.add_typer(docs_app, name="docs")


@app.command()
def generate(
    source_dir: Path | None = typer.Option(
        None,
        "--source_dir",
        "--source-dir",
        help="Directory containing stored results.",
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output_dir",
        "--output-dir",
        help="Directory for generated reports.",
    ),
    format: ReportFormat = typer.Option(
        ReportFormat.PDF,
        "--format",
        case_sensitive=False,
        help="Report output format.",
    ),
    mode: GenerateMode = typer.Option(
        GenerateMode.RUN,
        "--mode",
        case_sensitive=False,
        help="Generation mode.",
    ),
) -> None:
    load_config, generate_reports = build_generate_use_case()
    merged = load_config.execute(
        overrides={
            "source_dir": source_dir,
            "output_dir": output_dir,
            "format": format.value,
            "mode": mode.value,
        },
    )
    outputs = generate_reports.execute(merged)
    if not outputs:
        typer.echo("No results found.")
        raise typer.Exit(code=0)
    for report in outputs:
        typer.echo(str(report))


@app.command("build")
def build_command(
    input_dir: Path = typer.Option(Path("output/evidoc/metadata"), "--input-dir"),
    output_dir: Path = typer.Option(Path("output/evidoc/reports"), "--output-dir"),
    formats: str = typer.Option("pdf,docx", "--formats", help="Comma-separated: pdf,docx"),
    mode: GenerateMode = typer.Option(GenerateMode.SINGLE, "--mode", case_sensitive=False),
) -> None:
    for report in build(
        input_dir=input_dir,
        output_dir=output_dir,
        formats=[item.strip() for item in formats.split(",")],
        mode=mode.value,
    ):
        typer.echo(str(report))


@app.command()
def tui() -> None:
    EvidocTui().run()


@docs_app.command("robot-library")
def docs_robot_library() -> None:
    """Open the bundled Robot Framework keyword reference generated with libdoc."""

    document_path = open_documentation("robot-library")
    typer.echo(f"Opened bundled documentation: {document_path}")


@docs_app.command("manual")
def docs_manual() -> None:
    """Open the offline MkDocs manual bundled inside the installed wheel."""

    document_path = open_documentation("manual")
    typer.echo(f"Opened bundled documentation: {document_path}")


@docs_app.callback(invoke_without_command=True)
def docs_callback(ctx: typer.Context) -> None:
    """Print a short usage hint when `evidoc docs` is called without a subcommand."""

    if ctx.invoked_subcommand is not None:
        return
    typer.echo("Select a documentation target.")
    typer.echo(f"Available targets: {', '.join(available_documents())}")
    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()

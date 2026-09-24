from __future__ import annotations

from pathlib import Path

import typer

from evidoc import build, merge
from evidoc.documentation import available_documents, open_documentation
from evidoc.interfaces.tui.app import EvidocTui

app = typer.Typer(help="Evidoc reporting CLI.")
docs_app = typer.Typer(help="Open bundled Evidoc documentation.")
app.add_typer(docs_app, name="docs")


@app.command("build")
def build_command(
    input_dir: Path | None = typer.Option(None, "--input-dir"),
    output_dir: Path | None = typer.Option(None, "--output-dir"),
    formats: str | None = typer.Option(None, "--formats", help="Comma-separated: pdf,docx"),
    config: Path | None = typer.Option(None, "--config"),
    exclude_status: str | None = typer.Option(
        None, "--exclude-status", help="Comma-separated statuses, such as FAIL,SKIP"
    ),
    defects: list[str] | None = typer.Option(
        None, "--defect", help="Repeat BUG-123 for one case or 'Test name=BUG-123' for many"
    ),
) -> None:
    try:
        reports = build(
            input_dir=input_dir,
            output_dir=output_dir,
            formats=[item.strip() for item in formats.split(",")] if formats else None,
            config_path=config,
            exclude_status=exclude_status,
            defects=defects,
        )
    except (ValueError, FileNotFoundError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    for report in reports:
        typer.echo(str(report))


@app.command("merge")
def merge_command(
    input_dirs: list[Path] = typer.Option(..., "--input-dir", help="Repeat in attempt order"),
    output_dir: Path = typer.Option(..., "--output-dir"),
) -> None:
    typer.echo(str(merge(input_dirs, output_dir)))


@app.command()
def tui() -> None:
    EvidocTui().run()


@docs_app.command("library")
def docs_robot_library() -> None:
    """Open the bundled Robot Framework keyword reference generated with libdoc."""

    document_path = open_documentation("library")
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

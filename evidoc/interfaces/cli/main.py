from __future__ import annotations

from pathlib import Path

import typer

from evidoc.domain.enums import GenerateMode, ReportFormat
from evidoc.infrastructure.bootstrap import build_generate_use_case
from evidoc.interfaces.tui.app import EvidocTui

app = typer.Typer(help="Evidoc reporting CLI.")


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
            "format": ReportFormat.PDF.value,
            "mode": mode.value,
        },
    )
    outputs = generate_reports.execute(merged)
    if not outputs:
        typer.echo("No results found.")
        raise typer.Exit(code=0)
    for report in outputs:
        typer.echo(str(report))


@app.command()
def tui() -> None:
    EvidocTui().run()


if __name__ == "__main__":
    app()

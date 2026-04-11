from __future__ import annotations

from pathlib import Path

import typer

from evidoc.domain.enums import GenerateMode, ReportFormat
from evidoc.infrastructure.bootstrap import build_generate_use_case
from evidoc.interfaces.tui.app import EvidocTui

app = typer.Typer(help="Evidoc reporting CLI.")


@app.command()
def generate(
    source_dir: Path | None = typer.Option(None, "--source-dir", help="Directory containing stored results."),
    output_dir: Path | None = typer.Option(None, "--output-dir", help="Directory for generated reports."),
    format: ReportFormat | None = typer.Option(None, "--format", case_sensitive=False, help="Output format."),
    mode: GenerateMode | None = typer.Option(None, "--mode", case_sensitive=False, help="Generation mode."),
    config: Path | None = typer.Option(None, "--config", exists=True, dir_okay=False, file_okay=True, help="Config file path."),
) -> None:
    load_config, generate_reports = build_generate_use_case()
    merged = load_config.execute(
        config,
        overrides={
            "source_dir": source_dir,
            "output_dir": output_dir,
            "format": format.value if format else None,
            "mode": mode.value if mode else None,
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

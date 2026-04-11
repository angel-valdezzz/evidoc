from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, Footer, Header, Input, Select, Static

from evidoc.infrastructure.bootstrap import build_generate_use_case


class EvidocTui(App[None]):
    TITLE = "Evidoc"

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Static("Generate business-friendly evidence reports")
            yield Input(value="./results", id="source_dir", placeholder="Source directory")
            yield Input(value="./reports", id="output_dir", placeholder="Output directory")
            yield Select([("pdf", "pdf"), ("docx", "docx")], value="pdf", id="format")
            yield Select([("run", "run"), ("single", "single")], value="run", id="mode")
            yield Button("Generate", id="generate")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "generate":
            return
        source_dir = Path(self.query_one("#source_dir", Input).value)
        output_dir = Path(self.query_one("#output_dir", Input).value)
        format_value = self.query_one("#format", Select).value
        mode_value = self.query_one("#mode", Select).value
        load_config, generate_reports = build_generate_use_case()
        config = load_config.execute(
            overrides={
                "source_dir": source_dir,
                "output_dir": output_dir,
                "format": format_value,
                "mode": mode_value,
            }
        )
        outputs = generate_reports.execute(config)
        self.notify("Generated: " + ", ".join(str(path) for path in outputs) if outputs else "No results found")

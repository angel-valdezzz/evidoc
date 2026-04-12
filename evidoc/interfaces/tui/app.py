from __future__ import annotations

import subprocess
import sys
import threading
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.events import Resize
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static, TabbedContent, TabPane

from evidoc.infrastructure.bootstrap import build_generate_use_case


WELCOME_ART = r"""
 _______  _     _  _____  ______   _______  _______
 |______  |     |   |    |     \  |       | |
 |______  \_____/ __|__  |_____/  |_____  |_|_____
"""


class EvidocTui(App[None]):
    TITLE = "Evidoc"
    SUB_TITLE = "Evidence report generator"

    BINDINGS = [
        Binding("f1", "show_welcome", "Bienvenida"),
        Binding("f2", "show_operation", "Operacion"),
        Binding("ctrl+g", "generate_report", "Generar", show=False),
        Binding("ctrl+s", "browse_source", "Buscar origen", show=False),
        Binding("ctrl+o", "browse_output", "Buscar destino", show=False),
    ]

    CSS = """
    Screen {
        layout: vertical;
    }

    Header {
        background: $boost;
    }

    TabbedContent {
        height: 1fr;
    }

    TabPane {
        padding: 0;
    }

    ScrollableContainer {
        height: 1fr;
    }

    .panel {
        height: auto;
        border: ascii $primary;
        padding: 1 2;
        margin: 1 2;
    }

    .panel-title {
        text-style: bold;
        margin-bottom: 1;
    }

    .field-row {
        layout: horizontal;
        height: auto;
        margin-bottom: 1;
    }

    .field-label {
        width: 24;
        padding-top: 1;
        text-style: bold;
    }

    .field-input {
        width: 1fr;
        border: ascii $surface;
    }

    .field-input:focus {
        border: ascii $primary;
    }

    .browse-btn {
        width: 14;
        min-width: 14;
        margin-left: 1;
    }

    .hint {
        color: $text-muted;
        margin: 0 0 1 24;
    }

    .btn-row {
        height: auto;
        margin: 1 2;
    }

    .btn-row Button {
        width: 1fr;
    }

    #welcome-shell {
        align: center top;
        height: auto;
        margin: 1 2;
    }

    #welcome-art {
        width: 100%;
        text-align: center;
        content-align: center middle;
        text-style: bold;
        margin-bottom: 1;
    }

    #welcome-copy {
        width: 100%;
        content-align: center middle;
        color: $text-muted;
        margin-bottom: 1;
    }

    #welcome-actions,
    #welcome-notes {
        width: 100%;
    }

    #workspace {
        layout: horizontal;
        height: auto;
    }

    #workspace.-narrow {
        layout: vertical;
    }

    #form-panel {
        width: 2fr;
    }

    #summary-panel {
        width: 1fr;
    }

    #workspace.-narrow #form-panel,
    #workspace.-narrow #summary-panel {
        width: 1fr;
    }

    #workspace.-narrow .field-row {
        layout: vertical;
        margin-bottom: 2;
    }

    #workspace.-narrow .field-label {
        width: 100%;
        padding-top: 0;
    }

    #workspace.-narrow .hint {
        margin-left: 0;
    }

    #workspace.-narrow .browse-btn {
        width: 1fr;
        margin-left: 0;
        margin-top: 1;
    }

    #status {
        margin-top: 1;
        border: ascii $surface;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="welcome", id="tabs"):
            with TabPane("Bienvenida", id="welcome"):
                with ScrollableContainer():
                    with Vertical(id="welcome-shell"):
                        yield Static(WELCOME_ART.strip("\n"), id="welcome-art")
                        yield Static(
                            "Welcome to Evidoc. This console helps operators turn execution artifacts into stakeholder-ready evidence reports.",
                            id="welcome-copy",
                        )
                        with Container(classes="panel", id="welcome-actions"):
                            yield Static("Quick start", classes="panel-title")
                            yield Static("1. Press F2 to open Operacion.")
                            yield Static("2. Use Ctrl+S and Ctrl+O to pick the source and output folders.")
                            yield Static("3. Adjust format and mode according to the reporting target.")
                            yield Static("4. Press Ctrl+G or activate Generate report to run the process.")
                        with Container(classes="panel", id="welcome-notes"):
                            yield Static("Design notes", classes="panel-title")
                            yield Static("The TUI opens in Bienvenida by default.")
                            yield Static("The content area uses the full available space under the tabs.")
                            yield Static("The Operacion tab becomes vertical on smaller CMD windows.")
            with TabPane("Operacion", id="operation"):
                with ScrollableContainer():
                    with Container(id="workspace"):
                        with Vertical(classes="panel", id="form-panel"):
                            yield Static("Report setup", classes="panel-title")
                            with Horizontal(classes="field-row"):
                                yield Label("Source directory", classes="field-label")
                                yield Input(value="./results", id="source_dir", classes="field-input")
                                yield Button("Browse", id="browse_source", classes="browse-btn")
                            with Horizontal(classes="field-row"):
                                yield Label("Output directory", classes="field-label")
                                yield Input(value="./reports", id="output_dir", classes="field-input")
                                yield Button("Browse", id="browse_output", classes="browse-btn")
                            with Horizontal(classes="field-row"):
                                yield Label("Output format", classes="field-label")
                                yield Select([("PDF report", "pdf"), ("DOCX report", "docx")], value="pdf", id="format")
                            with Horizontal(classes="field-row"):
                                yield Label("Execution mode", classes="field-label")
                                yield Select(
                                    [("Complete run", "run"), ("Single result", "single")],
                                    value="run",
                                    id="mode",
                                )
                            yield Static(
                                "Shortcuts: F1 bienvenida, F2 operacion, Ctrl+S source folder, Ctrl+O output folder, Ctrl+G generate.",
                                classes="hint",
                            )
                            yield Static(
                                "Use complete run for batch execution or single result when you only need one evidence set.",
                                classes="hint",
                            )
                            with Horizontal(classes="btn-row"):
                                yield Button("Generate report", id="generate", variant="primary")
                        with Vertical(classes="panel", id="summary-panel"):
                            yield Static("Operator checklist", classes="panel-title")
                            yield Static("1. Confirm the source folder contains execution artifacts.")
                            yield Static("2. Choose the target folder where the report should be written.")
                            yield Static("3. Select the format required by the stakeholder.")
                            yield Static("4. Run generation and verify the resulting path notification.")
                            yield Static("Ready to generate with the current configuration.", id="status")
        yield Footer()

    def on_mount(self) -> None:
        self.action_show_welcome()
        self._sync_layout()

    def on_resize(self, event: Resize) -> None:
        self._sync_layout()

    def _sync_layout(self) -> None:
        if not self.is_mounted:
            return
        narrow = self.size.width <= 110
        self.query_one("#workspace").set_class(narrow, "-narrow")

    def _open_picker_in_subprocess(self, mode: str, title: str) -> str | None:
        if mode == "directory":
            code = (
                "import tkinter as tk; from tkinter import filedialog; "
                "root=tk.Tk(); root.withdraw(); root.attributes('-topmost', True); "
                f"print(filedialog.askdirectory(title={title!r}))"
            )
        else:
            return None
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=False)
        value = result.stdout.strip()
        return value or None

    def _browse_into_input(self, input_id: str, title: str) -> None:
        def pick() -> None:
            selected = self._open_picker_in_subprocess("directory", title)
            if selected:
                self.call_from_thread(self._apply_selected_path, input_id, selected)

        threading.Thread(target=pick, daemon=True).start()

    def _apply_selected_path(self, input_id: str, value: str) -> None:
        self.query_one(f"#{input_id}", Input).value = value
        self.notify(f"Selected: {value}")

    def _run_generation(self) -> None:
        self.action_show_operation()
        self.query_one("#status", Static).update("Generating report. Please wait...")
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
        message = "Generated: " + ", ".join(str(path) for path in outputs) if outputs else "No results found"
        self.query_one("#status", Static).update(message)
        self.notify(message)

    def action_show_welcome(self) -> None:
        self.query_one("#tabs", TabbedContent).active = "welcome"

    def action_show_operation(self) -> None:
        self.query_one("#tabs", TabbedContent).active = "operation"

    def action_browse_source(self) -> None:
        self.action_show_operation()
        self._browse_into_input("source_dir", "Select the source directory")

    def action_browse_output(self) -> None:
        self.action_show_operation()
        self._browse_into_input("output_dir", "Select the output directory")

    def action_generate_report(self) -> None:
        self._run_generation()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "browse_source":
            self.action_browse_source()
            return
        if event.button.id == "browse_output":
            self.action_browse_output()
            return
        if event.button.id == "generate":
            self._run_generation()

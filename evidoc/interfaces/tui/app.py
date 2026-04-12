from __future__ import annotations

import subprocess
import sys
import threading
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.events import Resize
from textual.reactive import reactive
from textual.widgets import Button, Header, Input, Label, Static, TabbedContent, TabPane

from evidoc.infrastructure.bootstrap import build_generate_use_case


WELCOME_ART = r"""
######## #     # ##### ######  ####   #####
#        #     #   #   #     # #   # #     
#####    #     #   #   #     # #   # #     
#         #   #    #   #     # #   # #     
#          # #     #   #     # #   # #     
########    #    ##### ######  ####   #####
"""


class EvidocTui(App[None]):
    TITLE = "Evidoc"
    SUB_TITLE = "Evidence report generator"
    ENABLE_COMMAND_PALETTE = False
    selected_format = reactive("pdf")
    selected_mode = reactive("run")

    BINDINGS = [
        Binding("f1", "show_welcome", "Bienvenida"),
        Binding("f2", "show_operation", "Operacion"),
        Binding("ctrl+p", "noop", "", show=False, priority=True),
        Binding("ctrl+g", "generate_report", "Generar", show=False),
        Binding("ctrl+s", "browse_source", "Buscar origen", show=False),
        Binding("ctrl+o", "browse_output", "Buscar destino", show=False),
    ]

    CSS = """
    Screen {
        background: $surface;
    }

    Header {
        dock: top;
        height: 1;
        background: $panel-darken-1;
        color: $text;
    }

    #topbar {
        dock: top;
        height: 1;
        padding: 0 2;
        background: $surface-lighten-1;
        color: $text-muted;
    }

    #bottombar {
        dock: bottom;
        height: 1;
        padding: 0 2;
        background: $panel-darken-1;
        color: $text;
    }

    TabbedContent {
        width: 1fr;
        dock: top;
        height: 1fr;
    }

    Tabs {
        background: $surface;
        color: $text-muted;
        padding: 0 1;
    }

    Tabs:focus {
        border: none;
    }

    Tab {
        padding: 0 1;
        margin-right: 1;
        background: transparent;
        border: none;
        color: $text-muted;
    }

    Tab.-active {
        background: $primary 20%;
        color: $text;
        text-style: bold;
    }

    TabPane {
        padding: 0;
        background: $surface;
    }

    ScrollableContainer {
        height: 1fr;
        background: $surface;
    }

    .panel {
        height: auto;
        border: none;
        background: $panel;
        padding: 1 2;
        margin: 1 2;
    }

    .panel-title {
        text-style: bold;
        margin-bottom: 1;
        color: $text;
    }

    .field-row {
        layout: horizontal;
        height: auto;
        align: left middle;
        margin-bottom: 1;
    }

    .field-label {
        width: 24;
        padding-top: 1;
        text-style: bold;
        color: $text;
    }

    .field-input {
        width: 1fr;
        height: 3;
        border: none;
        background: $surface-lighten-1;
        padding: 0 1;
        color: $text;
    }

    .field-input:focus {
        background: $surface-lighten-2;
        tint: $primary 8%;
    }

    .browse-btn {
        width: 14;
        min-width: 14;
        height: 3;
        margin-left: 1;
        border: none;
        background: $surface-lighten-1;
        color: $text;
    }

    .choice-group {
        layout: horizontal;
        width: 1fr;
        height: auto;
    }

    .choice-button {
        width: 1fr;
        height: 3;
        margin-right: 1;
        border: none;
        background: $surface-lighten-1;
        color: $text-muted;
    }

    .choice-button.last {
        margin-right: 0;
    }

    .choice-button.-selected {
        background: $primary 20%;
        color: $text;
        text-style: bold;
    }

    .btn-row Button {
        height: 3;
    }

    Button {
        border: none;
        background: $surface-lighten-1;
        color: $text;
    }

    Button:hover {
        background: $surface-lighten-2;
    }

    Button:focus {
        background: $primary 22%;
        color: $text;
        text-style: bold;
    }

    #generate {
        background: $primary;
        color: $text;
        text-style: bold;
    }

    #generate:hover {
        background: $primary-darken-1;
    }

    #generate:focus {
        background: $primary-darken-1;
        text-style: bold;
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

    #workspace.-narrow .choice-group {
        layout: vertical;
    }

    #workspace.-narrow .choice-button {
        margin-right: 0;
        margin-bottom: 1;
    }

    #workspace.-narrow .choice-button.last {
        margin-bottom: 0;
    }

    #status {
        margin-top: 1;
        border: none;
        background: $surface-lighten-1;
        padding: 1;
        color: $text;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "Navigate with F1/F2. Use Ctrl+S and Ctrl+O to pick folders. Press Ctrl+G to generate.",
            id="topbar",
        )
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
                            yield Static("1. Open the Operacion tab when you are ready to configure a report.")
                            yield Static("2. Pick the source and output folders.")
                            yield Static("3. Choose the report format and execution mode.")
                            yield Static("4. Generate the report and confirm the resulting output.")
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
                                with Horizontal(classes="choice-group"):
                                    yield Button("PDF report", id="format_pdf", classes="choice-button")
                                    yield Button("DOCX report", id="format_docx", classes="choice-button last")
                            with Horizontal(classes="field-row"):
                                yield Label("Execution mode", classes="field-label")
                                with Horizontal(classes="choice-group"):
                                    yield Button("Complete run", id="mode_run", classes="choice-button")
                                    yield Button("Single result", id="mode_single", classes="choice-button last")
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
        yield Static("F1 Bienvenida   F2 Operacion   Ctrl+S Buscar origen   Ctrl+O Buscar destino   Ctrl+G Generar", id="bottombar")
    def on_mount(self) -> None:
        self.action_show_welcome()
        self._refresh_choices()
        self._sync_layout()

    def on_resize(self, event: Resize) -> None:
        self._sync_layout()

    def _sync_layout(self) -> None:
        if not self.is_mounted:
            return
        narrow = self.size.width <= 110
        self.query_one("#workspace").set_class(narrow, "-narrow")

    def _refresh_choices(self) -> None:
        if not self.is_mounted:
            return
        self.query_one("#format_pdf", Button).set_class(self.selected_format == "pdf", "-selected")
        self.query_one("#format_docx", Button).set_class(self.selected_format == "docx", "-selected")
        self.query_one("#mode_run", Button).set_class(self.selected_mode == "run", "-selected")
        self.query_one("#mode_single", Button).set_class(self.selected_mode == "single", "-selected")

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
        format_value = self.selected_format
        mode_value = self.selected_mode
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

    def action_noop(self) -> None:
        return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "format_pdf":
            self.selected_format = "pdf"
            self._refresh_choices()
            return
        if event.button.id == "format_docx":
            self.selected_format = "docx"
            self._refresh_choices()
            return
        if event.button.id == "mode_run":
            self.selected_mode = "run"
            self._refresh_choices()
            return
        if event.button.id == "mode_single":
            self.selected_mode = "single"
            self._refresh_choices()
            return
        if event.button.id == "browse_source":
            self.action_browse_source()
            return
        if event.button.id == "browse_output":
            self.action_browse_output()
            return
        if event.button.id == "generate":
            self._run_generation()

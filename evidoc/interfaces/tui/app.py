from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, VerticalScroll
from textual.events import Resize
from textual.widgets import Button, ContentSwitcher, Footer, Header, Input, Label, Select, Static, Tab, Tabs

from evidoc.infrastructure.bootstrap import build_generate_use_case


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

    #shell {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
    }

    #hero {
        margin-bottom: 1;
    }

    #hero_title {
        text-style: bold;
    }

    #hero_copy {
        color: $text-muted;
    }

    #main_tabs {
        height: auto;
        margin-bottom: 1;
    }

    #main_content {
        height: 1fr;
    }

    #main_content > .tab-screen {
        padding: 0;
    }

    #welcome_scroll,
    #operation_scroll {
        height: 1fr;
        width: 1fr;
    }

    #workspace_body {
        layout: horizontal;
        width: 1fr;
        height: auto;
    }

    #workspace_body.-narrow {
        layout: vertical;
    }

    .panel {
        width: 1fr;
        height: auto;
        padding: 1 2;
        border: ascii $primary;
    }

    #form_panel {
        width: 2fr;
        margin-right: 1;
    }

    #form_panel.-stack {
        margin-right: 0;
        margin-bottom: 1;
    }

    #summary_panel {
        width: 1fr;
    }

    .section_title {
        text-style: bold;
        margin-bottom: 1;
    }

    .field {
        margin-bottom: 1;
    }

    .field Label {
        margin-bottom: 1;
    }

    .path_row {
        layout: horizontal;
        width: 1fr;
        height: 3;
        align: left middle;
    }

    .path_row.-stack {
        layout: vertical;
        height: auto;
    }

    .path_input {
        width: 1fr;
        margin-right: 1;
        height: 3;
    }

    .path_row.-stack .path_input {
        margin-right: 0;
        margin-bottom: 1;
    }

    .browse_button {
        width: 16;
        min-width: 16;
        height: 3;
    }

    .hint {
        color: $text-muted;
        margin-top: 1;
    }

    Select,
    Input,
    Button {
        width: 1fr;
        height: 3;
        border: ascii $surface;
    }

    Select:focus,
    Input:focus,
    Button:focus {
        border: ascii $primary;
    }

    #generate {
        width: 100%;
        margin-top: 1;
    }

    #status {
        margin-top: 1;
        padding: 1;
        border: ascii $surface-lighten-1;
    }

    #welcome_panel {
        padding: 1 2;
    }

    #ascii_art {
        text-style: bold;
        margin-bottom: 1;
    }

    #welcome_copy {
        color: $text-muted;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="shell"):
            with Vertical(id="hero"):
                yield Static("Evidence operations console", id="hero_title")
                yield Static(
                    "Configure the input folders and output format before generating the final evidence package. ASCII layout mode keeps the interface stable in basic Windows CMD.",
                    id="hero_copy",
                )
            yield Tabs(
                Tab("Bienvenida", id="tab-welcome"),
                Tab("Operacion", id="tab-operation"),
                id="main_tabs",
                active="tab-welcome",
            )
            with ContentSwitcher(initial="welcome", id="main_content"):
                with VerticalScroll(id="welcome", classes="tab-screen welcome-screen"):
                    with Vertical(classes="panel", id="welcome_panel"):
                        yield Static(
                            r"""
  ________   ___      ___   ________   ________   ________
 |\   ____\ |\  \    /  /| |\   ___  \|\   ___  \|\   ____\
 \ \  \___| \ \  \  /  / / \ \  \\ \  \ \  \\ \  \ \  \___|
  \ \  \     \ \  \/  / /   \ \  \\ \  \ \  \\ \  \ \  \
   \ \  \____ \ \    / /     \ \  \\ \  \ \  \\ \  \ \  \____
    \ \_______\\ \__/ /       \ \__\\ \__\ \__\\ \__\ \_______\
     \|_______| \|__|/         \|__| \|__|\|__| \|__|\|_______|
                            """.strip("\n"),
                            id="ascii_art",
                        )
                        yield Static(
                            "Welcome to Evidoc. This console helps operators turn execution artifacts into stakeholder-ready evidence reports.",
                            id="welcome_copy",
                        )
                        yield Static("Quick start", classes="section_title")
                        yield Static("1. Press F2 to open Operacion.")
                        yield Static("2. Use Ctrl+S and Ctrl+O to pick the source and output folders.")
                        yield Static("3. Adjust format and mode according to the reporting target.")
                        yield Static("4. Press Ctrl+G or activate Generate report to run the process.")
                with VerticalScroll(id="operation", classes="tab-screen operation-screen"):
                    with Container(id="workspace_body"):
                        with Vertical(classes="panel", id="form_panel"):
                            yield Static("Report setup", classes="section_title")
                            with Vertical(classes="field"):
                                yield Label("Source directory")
                                with Container(classes="path_row", id="source_path_row"):
                                    yield Input(
                                        value="./results",
                                        id="source_dir",
                                        placeholder="Example: ./results",
                                        classes="path_input",
                                    )
                                    yield Button("Browse", id="browse_source", classes="browse_button")
                            with Vertical(classes="field"):
                                yield Label("Output directory")
                                with Container(classes="path_row", id="output_path_row"):
                                    yield Input(
                                        value="./reports",
                                        id="output_dir",
                                        placeholder="Example: ./reports",
                                        classes="path_input",
                                    )
                                    yield Button("Browse", id="browse_output", classes="browse_button")
                            with Vertical(classes="field"):
                                yield Label("Output format")
                                yield Select([("PDF report", "pdf"), ("DOCX report", "docx")], value="pdf", id="format")
                            with Vertical(classes="field"):
                                yield Label("Execution mode")
                                yield Select(
                                    [("Complete run", "run"), ("Single result", "single")],
                                    value="run",
                                    id="mode",
                                )
                            yield Static(
                                "Shortcuts: F1 welcome, F2 operation, Ctrl+S source folder, Ctrl+O output folder, Ctrl+G generate.",
                                classes="hint",
                            )
                            yield Static(
                                "Use complete run for batch execution or single result when you only need one evidence set.",
                                classes="hint",
                            )
                            yield Button("Generate report", id="generate", variant="primary")
                        with Vertical(classes="panel", id="summary_panel"):
                            yield Static("Operator checklist", classes="section_title")
                            yield Static("1. Confirm the source folder contains execution artifacts.")
                            yield Static("2. Choose the target folder where the report should be written.")
                            yield Static("3. Select the format required by the stakeholder.")
                            yield Static("4. Run generation and verify the resulting path notification.")
                            yield Static("Ready to generate with the current configuration.", id="status")
        yield Footer()

    def on_mount(self) -> None:
        self._set_active_tab("welcome")
        self._sync_layout()

    def on_resize(self, event: Resize) -> None:
        self._sync_layout()

    def _sync_layout(self) -> None:
        if not self.is_mounted:
            return
        narrow = self.size.width < 150
        self.query_one("#workspace_body").set_class(narrow, "-narrow")
        self.query_one("#source_path_row").set_class(narrow, "-stack")
        self.query_one("#output_path_row").set_class(narrow, "-stack")
        self.query_one("#form_panel").set_class(narrow, "-stack")

    def _set_active_tab(self, tab_id: str) -> None:
        tab_widget_id = "tab-welcome" if tab_id == "welcome" else "tab-operation"
        self.query_one("#main_tabs", Tabs).active = tab_widget_id
        self.query_one("#main_content", ContentSwitcher).current = tab_id

    def _pick_directory(self, title: str) -> str | None:
        try:
            from tkinter import Tk, filedialog
        except ImportError:
            self.notify("File dialog is not available in this environment.", severity="error")
            return None

        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        root.update()
        try:
            selected = filedialog.askdirectory(title=title)
        finally:
            root.destroy()
        return selected or None

    def _browse_into_input(self, input_id: str, title: str) -> None:
        selected_path = self._pick_directory(title)
        if selected_path:
            self.query_one(f"#{input_id}", Input).value = selected_path
            self.notify(f"Selected: {selected_path}")

    def _run_generation(self) -> None:
        self._set_active_tab("operation")
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
        self._set_active_tab("welcome")

    def action_show_operation(self) -> None:
        self._set_active_tab("operation")

    def action_browse_source(self) -> None:
        self._set_active_tab("operation")
        self._browse_into_input("source_dir", "Select the source directory")

    def action_browse_output(self) -> None:
        self._set_active_tab("operation")
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

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        content_id = "welcome" if event.tab.id == "tab-welcome" else "operation"
        self.query_one("#main_content", ContentSwitcher).current = content_id

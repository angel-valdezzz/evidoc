from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static

from evidoc.infrastructure.bootstrap import build_generate_use_case


class EvidocTui(App[None]):
    TITLE = "Evidoc"
    SUB_TITLE = "Evidence report generator"
    active_tab = reactive("welcome")

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

    #workspace {
        height: 1fr;
    }

    #tabs {
        margin-bottom: 1;
        height: auto;
    }

    .tab-button {
        width: auto;
        min-width: 18;
        margin-right: 1;
        border: ascii $surface;
    }

    .tab-button.-active {
        border: ascii $primary;
        background: $primary 15%;
        text-style: bold;
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

    #summary_panel {
        width: 1fr;
    }

    .tab-panel {
        display: none;
        height: 1fr;
    }

    .tab-panel.-visible {
        display: block;
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

    .hint {
        color: $text-muted;
        margin-top: 1;
    }

    Select, Input, Button {
        width: 1fr;
        border: ascii $surface;
    }

    Select:focus, Input:focus, Button:focus {
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
            with Horizontal(id="tabs"):
                yield Button("Bienvenida", id="tab_welcome", classes="tab-button")
                yield Button("Generacion", id="tab_generate", classes="tab-button")
            with Container(id="workspace"):
                with Vertical(classes="panel tab-panel", id="welcome_panel"):
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
                    yield Static("Recommended flow", classes="section_title")
                    yield Static("1. Open the Generacion tab.")
                    yield Static("2. Point to the source and output folders.")
                    yield Static("3. Choose the output format and execution mode.")
                    yield Static("4. Generate the report and confirm the resulting path.")
                with Vertical(classes="tab-panel -visible", id="generate_panel"):
                    with Horizontal(id="workspace_body"):
                        with Vertical(classes="panel", id="form_panel"):
                            yield Static("Report setup", classes="section_title")
                            with Vertical(classes="field"):
                                yield Label("Source directory")
                                yield Input(value="./results", id="source_dir", placeholder="Example: ./results")
                            with Vertical(classes="field"):
                                yield Label("Output directory")
                                yield Input(value="./reports", id="output_dir", placeholder="Example: ./reports")
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
        self._refresh_tabs()

    def watch_active_tab(self) -> None:
        self._refresh_tabs()

    def _refresh_tabs(self) -> None:
        if not self.is_mounted:
            return
        self.query_one("#tab_welcome", Button).set_class(self.active_tab == "welcome", "-active")
        self.query_one("#tab_generate", Button).set_class(self.active_tab == "generate", "-active")
        self.query_one("#welcome_panel").set_class(self.active_tab == "welcome", "-visible")
        self.query_one("#generate_panel").set_class(self.active_tab == "generate", "-visible")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "tab_welcome":
            self.active_tab = "welcome"
            return
        if event.button.id == "tab_generate":
            self.active_tab = "generate"
            return
        if event.button.id != "generate":
            return
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

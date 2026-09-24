from __future__ import annotations

from pathlib import Path

import pytest
from evidoc.documentation import available_documents, resolve_document_path
from evidoc.interfaces.cli.main import app
from typer.testing import CliRunner

pytestmark = pytest.mark.unit


def test_available_documents_lists_robot_library() -> None:
    assert "library" in available_documents()
    assert "manual" in available_documents()


def test_resolve_document_path_returns_bundled_manual_index() -> None:
    path = resolve_document_path("manual")

    assert isinstance(path, Path)
    assert path.exists()
    assert path.name == "index.html"


def test_resolve_document_path_returns_bundled_robot_libdoc() -> None:
    path = resolve_document_path("library")

    assert isinstance(path, Path)
    assert path.exists()
    assert path.name == "robot-library.html"


def test_resolve_document_path_rejects_unknown_document() -> None:
    with pytest.raises(ValueError):
        resolve_document_path("missing-doc")


def test_cli_lists_only_current_commands_and_document_names() -> None:
    runner = CliRunner()
    help_text = runner.invoke(app, ["--help"])
    docs_text = runner.invoke(app, ["docs"])
    assert help_text.exit_code == docs_text.exit_code == 0
    assert "build" in help_text.stdout and "merge" in help_text.stdout
    assert "generate" not in help_text.stdout
    assert "Available targets: library, manual" in docs_text.stdout

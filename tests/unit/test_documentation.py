from __future__ import annotations

from pathlib import Path

import pytest

from evidoc.documentation import available_documents, resolve_document_path

pytestmark = pytest.mark.unit


def test_available_documents_lists_robot_library() -> None:
    assert "robot-library" in available_documents()


def test_resolve_document_path_returns_bundled_robot_libdoc() -> None:
    path = resolve_document_path("robot-library")

    assert isinstance(path, Path)
    assert path.exists()
    assert path.name == "robot-library.html"


def test_resolve_document_path_rejects_unknown_document() -> None:
    with pytest.raises(ValueError):
        resolve_document_path("missing-doc")

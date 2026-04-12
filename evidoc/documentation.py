from __future__ import annotations

"""Helpers for bundled documentation assets distributed with Evidoc."""

import os
import shutil
import subprocess
import sys
import tempfile
import webbrowser
from importlib import resources
from pathlib import Path

_DOCS_ROOT = ("resources", "docs")
_BUNDLED_DOCS = {
    "robot-library": "robot-library.html",
}


def available_documents() -> tuple[str, ...]:
    """Return the public documentation identifiers exposed by the CLI."""

    return tuple(sorted(_BUNDLED_DOCS))


def resolve_document_path(name: str) -> Path:
    """Return a filesystem path for a bundled documentation asset.

    A wheel installed by ``pip`` is normally unpacked on disk, but this helper
    still falls back to a temporary copy when the resource comes from a
    non-filesystem loader.
    """

    filename = _BUNDLED_DOCS.get(name)
    if filename is None:
        raise ValueError(f"Unknown bundled document '{name}'.")

    traversable = resources.files("evidoc")
    for segment in (*_DOCS_ROOT, filename):
        traversable = traversable.joinpath(segment)

    if isinstance(traversable, Path):
        return traversable

    suffix = Path(filename).suffix
    temp_root = Path(tempfile.gettempdir()) / "evidoc-docs"
    temp_root.mkdir(parents=True, exist_ok=True)
    destination = temp_root / f"{name}{suffix}"
    with traversable.open("rb") as source, destination.open("wb") as target:
        shutil.copyfileobj(source, target)
    return destination


def open_documentation(name: str) -> Path:
    """Open a bundled documentation asset with the local operating system."""

    document_path = resolve_document_path(name)
    if not document_path.exists():
        raise FileNotFoundError(f"Bundled document '{name}' was not found at '{document_path}'.")

    if os.name == "nt":
        os.startfile(str(document_path))
        return document_path
    if sys.platform == "darwin":
        subprocess.run(["open", str(document_path)], check=True)
        return document_path
    if shutil.which("xdg-open"):
        subprocess.run(["xdg-open", str(document_path)], check=True)
        return document_path
    if webbrowser.open(document_path.as_uri()):
        return document_path
    raise RuntimeError(f"Unable to open bundled document '{document_path}'.")

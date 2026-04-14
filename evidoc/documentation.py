"""Helpers for bundled documentation assets distributed with Evidoc."""

import os
import shutil
import subprocess
import sys
import tempfile
import webbrowser
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path

_DOCS_ROOT = ("resources", "docs")
_BUNDLED_DOCS = {
    "manual": ("site", "index.html"),
    "robot-library": ("robot-library.html",),
}


def available_documents() -> tuple[str, ...]:
    """Return the public documentation identifiers exposed by the CLI."""

    return tuple(sorted(_BUNDLED_DOCS))


def _copy_traversable_to_path(source: Traversable, destination: Path) -> None:
    if source.is_dir():
        destination.mkdir(parents=True, exist_ok=True)
        for child in source.iterdir():
            _copy_traversable_to_path(child, destination / child.name)
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as source_file, destination.open("wb") as target_file:
        shutil.copyfileobj(source_file, target_file)


def _resource_path(*segments: str) -> Path:
    traversable: Traversable = resources.files("evidoc")
    parent = traversable
    for segment in (*_DOCS_ROOT, *segments):
        parent = traversable
        traversable = traversable.joinpath(segment)

    if isinstance(traversable, Path):
        return traversable

    temp_root = Path(tempfile.gettempdir()) / "evidoc-docs"
    copy_root = temp_root / Path(*segments[:-1]) if len(segments) > 1 else temp_root
    if copy_root.exists():
        shutil.rmtree(copy_root)
    source = traversable if len(segments) == 1 else parent
    _copy_traversable_to_path(source, copy_root)
    return copy_root / segments[-1]


def resolve_document_path(name: str) -> Path:
    """Return a filesystem path for a bundled documentation asset.

    A wheel installed by ``pip`` is normally unpacked on disk, but this helper
    still falls back to a temporary copy when the resource comes from a
    non-filesystem loader.
    """

    resource_segments = _BUNDLED_DOCS.get(name)
    if resource_segments is None:
        raise ValueError(f"Unknown bundled document '{name}'.")
    return _resource_path(*resource_segments)


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

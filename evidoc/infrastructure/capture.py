"""Capture adapters. The result model only receives PNG bytes."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any


def screenshot_bytes(target: Any) -> bytes:
    """Support Selenium WebDriver/WebElement and screenshot-compatible drivers."""
    if hasattr(target, "screenshot_as_png"):
        return bytes(target.screenshot_as_png)
    if hasattr(target, "get_screenshot_as_png"):
        return bytes(target.get_screenshot_as_png())
    with TemporaryDirectory() as directory:
        destination = Path(directory) / "capture.png"
        method = getattr(target, "screenshot", None) or getattr(target, "save_screenshot", None)
        if method is None or method(str(destination)) is False:
            raise RuntimeError("Target does not support screenshot capture")
        return destination.read_bytes()


def desktop_bytes() -> bytes:
    """Capture the virtual desktop independently of browser automation."""
    import mss
    import mss.tools

    with mss.mss() as screen:
        monitor = screen.monitors[0]
        shot = screen.grab(monitor)
        data = mss.tools.to_png(shot.rgb, shot.size)
        if data is None:
            raise RuntimeError("Desktop capture produced no image")
        return bytes(data)

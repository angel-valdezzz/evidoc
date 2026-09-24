from __future__ import annotations

import re


def safe_name(name: str) -> str:
    """Turn a case title into a portable report filename stem."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._") or "test"

"""Shared environment loading helpers."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent


def load_env(env_path: str | Path | None = None) -> None:
    """Load simple KEY=VALUE pairs from .env without overwriting process env."""
    path = Path(env_path) if env_path else PROJECT_ROOT / ".env"
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

"""Resolve KARMA project root and standard directories."""
from __future__ import annotations

import os
from pathlib import Path

# scripts/ -> repo root
KARMA_ROOT = Path(os.environ.get("KARMA_ROOT", Path(__file__).resolve().parent.parent))

MEMORY_DIR = KARMA_ROOT / "memory"
PROMPTS_DIR = KARMA_ROOT / "prompts"
LOGS_DIR = KARMA_ROOT / "logs"
EXPERIENCE_DIR = KARMA_ROOT / "experience"
HISTORY_DIR = KARMA_ROOT / "history_tasks"
SCRIPTS_DIR = KARMA_ROOT / "scripts"
RESOURCES_DIR = KARMA_ROOT / "resources"


def p(*parts: str) -> str:
    """Join under KARMA_ROOT and return a string path."""
    return str(KARMA_ROOT.joinpath(*parts))

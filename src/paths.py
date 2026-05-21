"""Resolve KARMA project root and standard directories."""
from __future__ import annotations

import os
from pathlib import Path

# src/ -> repo root
KARMA_ROOT = Path(os.environ.get("KARMA_ROOT", Path(__file__).resolve().parent.parent))

MEMORY_DIR = KARMA_ROOT / "memory"
PROMPTS_DIR = KARMA_ROOT / "prompts"
LOGS_DIR = KARMA_ROOT / "logs"
EXPERIENCE_DIR = KARMA_ROOT / "experience"
HISTORY_DIR = KARMA_ROOT / "history_tasks"
SCRIPTS_DIR = KARMA_ROOT / "scripts"
RESOURCES_DIR = KARMA_ROOT / "resources"
ARTIFACTS_DIR = KARMA_ROOT / "artifacts"
TASK_FUNCTIONS_PATH = KARMA_ROOT / "src" / "env" / "task_functions.py"


def ensure_runtime_dirs() -> None:
    for d in (MEMORY_DIR, PROMPTS_DIR, LOGS_DIR, MEMORY_DIR / "short_term", ARTIFACTS_DIR):
        d.mkdir(parents=True, exist_ok=True)


def ensure_runtime_env() -> None:
    """Env vars required for AI2-THOR CloudRendering on headless NVIDIA servers."""
    os.environ.setdefault("VK_ICD_FILENAMES", "/etc/vulkan/icd.d/nvidia_icd.json")


def ensure_hf_mirror() -> None:
    """Use HF mirror by default to avoid huggingface.co timeouts in CN."""
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")


def p(*parts: str) -> str:
    """Join under KARMA_ROOT and return a string path."""
    return str(KARMA_ROOT.joinpath(*parts))

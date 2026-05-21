"""Repo-relative paths for portable KARMA runs."""
from __future__ import annotations

import os
from pathlib import Path

_DEFAULT_ROOT = Path(__file__).resolve().parent.parent
KARMA_ROOT = Path(os.environ.get("KARMA_ROOT", _DEFAULT_ROOT)).resolve()


def resolve(path: str | Path) -> Path:
    """Resolve a path relative to the repo root."""
    p = Path(path)
    if p.is_absolute():
        return p
    return (KARMA_ROOT / p).resolve()


def ensure_repo_cwd() -> None:
    """Run from repo root so relative paths behave consistently."""
    os.chdir(KARMA_ROOT)


def load_dotenv() -> None:
    """Load repo .env into os.environ (setdefault, never overrides)."""
    env_file = resolve(".env")
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


# Directory aliases (prefer resolve("memory/...") for file I/O)
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
    for rel in (
        "memory",
        "memory/short_term",
        "prompts",
        "logs",
        "artifacts",
        "artifacts/logs",
        "artifacts/benchmark",
        "artifacts/sim",
    ):
        resolve(rel).mkdir(parents=True, exist_ok=True)


def ensure_runtime_env() -> None:
    """Env vars required for AI2-THOR CloudRendering on headless NVIDIA servers."""
    os.environ.setdefault("VK_ICD_FILENAMES", "/etc/vulkan/icd.d/nvidia_icd.json")


def ensure_hf_mirror() -> None:
    """Use HF mirror by default to avoid huggingface.co timeouts in CN."""
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")


def p(*parts: str) -> str:
    """Join path parts as a repo-relative string."""
    return str(Path(*parts))

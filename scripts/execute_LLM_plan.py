"""Backward-compatible wrapper. Loads executor side effects (task thread)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("KARMA_ROOT", ROOT)

from src.env import executor  # noqa: F401

if __name__ == "__main__":
    executor.run_scripts()

"""Backward-compatible wrapper."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("KARMA_ROOT", ROOT)

from src.memory.retrieval import main

if __name__ == "__main__":
    main()

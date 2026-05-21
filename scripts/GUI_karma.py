#!/usr/bin/env python3
"""Backward-compatible GUI entry. Prefer `python main.py base --task.use_gui`."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("KARMA_ROOT", ROOT)

from src.env.gui import launch_gui

if __name__ == "__main__":
    launch_gui()

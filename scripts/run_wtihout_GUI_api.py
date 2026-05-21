#!/usr/bin/env python3
"""Backward-compatible benchmark entry. Prefer `python main.py benchmark`."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("KARMA_ROOT", ROOT)

from src.benchmark.eval import run_benchmark

if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "long_task_3"
    run_benchmark(task_name=task, output_path=f"artifacts/{task}_output.json")

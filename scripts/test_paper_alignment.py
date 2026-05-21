#!/usr/bin/env python3
"""Offline tests for paper-aligned KARMA modules (no API / sim required)."""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.memory.replacement import apply_replacement
from src.memory.ltm_graph import serialize_graph_for_prompt
from src.benchmark.alfred_l import validate_alfred_l_dataset


def test_fifo_merge():
    existing = [{"objectId": "a", "objectType": "Apple", "timestamp": 1.0}]
    new = [{"objectId": "b", "objectType": "Tomato", "timestamp": 2.0}]
    out = apply_replacement(existing, new, policy="fifo", max_objects=100)
    assert len(out) == 2
    new2 = [{"objectId": "a", "objectType": "Apple", "position": {"x": 1}, "timestamp": 3.0}]
    out2 = apply_replacement(out, new2, policy="fifo", max_objects=100)
    assert len(out2) == 2
    assert out2[-1]["objectId"] == "a"


def test_ltm_serialization():
    graph = {
        "floor": {
            "name": "floor 1",
            "scene": "FloorPlan1",
            "areas": [
                {
                    "name": "node 1",
                    "type": "Area",
                    "position": [1.0, 0.0, 2.0],
                    "contains": ["Fridge"],
                    "adjacent_nodes": ["node 2"],
                    "objects": [],
                }
            ],
        }
    }
    text = serialize_graph_for_prompt(graph)
    assert "adjacent nodes: [node 2]" in text
    assert "contains: [Fridge]" in text


def test_alfred_l_counts():
    report = validate_alfred_l_dataset()
    assert report["valid"] is True
    assert report["total_tasks"] == 48


def main() -> int:
    test_fifo_merge()
    test_ltm_serialization()
    test_alfred_l_counts()
    print("paper alignment unit tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

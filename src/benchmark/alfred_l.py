"""ALFRED-L benchmark loader and evaluation harness (paper Sec. V)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.paths import resolve


def _load_category(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    key = next(iter(data.keys()))
    return list(data[key])


def load_alfred_l_tasks(category: str = "all") -> list[dict[str, Any]]:
    root = resolve("ALFRED_L")
    mapping = {
        "simple": root / "simple_tasks.json",
        "composite": root / "composite_tasks.json",
        "complex": root / "complex_tasks.json",
    }
    if category == "all":
        tasks: list[dict[str, Any]] = []
        for name, path in mapping.items():
            for t in _load_category(path):
                t = dict(t)
                t["category"] = name
                tasks.append(t)
        return tasks
    return [dict(t, category=category) for t in _load_category(mapping[category])]


def validate_alfred_l_dataset() -> dict[str, Any]:
    tasks = load_alfred_l_tasks("all")
    by_cat: dict[str, int] = {}
    for t in tasks:
        by_cat[t.get("category", "?")] = by_cat.get(t.get("category", "?"), 0) + 1
    return {
        "total_tasks": len(tasks),
        "by_category": by_cat,
        "expected_total": 48,
        "expected_simple": 15,
        "expected_composite": 15,
        "expected_complex": 18,
        "valid": len(tasks) == 48 and by_cat.get("simple") == 15,
    }


def run_alfred_l_suite(
    category: str = "all",
    *,
    dry_run: bool = True,
    limit: int | None = None,
) -> dict[str, Any]:
    """Load ALFRED-L tasks; dry_run validates dataset and returns task manifest."""
    tasks = load_alfred_l_tasks(category)
    if limit is not None:
        tasks = tasks[:limit]

    manifest = [
        {
            "id": t.get("ID"),
            "floor_plan": t.get("FloorPlan"),
            "instruction": t.get("Instruction", "").strip(),
            "goal": t.get("Goal Condition", ""),
            "category": t.get("category"),
        }
        for t in tasks
    ]

    report = validate_alfred_l_dataset()
    report["manifest_count"] = len(manifest)
    report["dry_run"] = dry_run
    report["tasks"] = manifest if dry_run else manifest[:5]

    out = resolve("artifacts/alfred_l_manifest.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report

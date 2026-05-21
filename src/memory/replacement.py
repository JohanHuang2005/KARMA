"""Short-term memory replacement policies (KARMA paper Sec. IV-D)."""
from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any, Literal

Policy = Literal["fifo", "lfu", "wtinylfu"]


def _stamp(entry: dict[str, Any]) -> dict[str, Any]:
    out = dict(entry)
    out.setdefault("timestamp", time.time())
    out.setdefault("access_count", 0)
    return out


def merge_fifo(existing: list[dict], new_entries: list[dict], max_objects: int) -> list[dict]:
    """Paper-improved FIFO: merge by objectId, evict oldest when over capacity."""
    merged: OrderedDict[str, dict] = OrderedDict()
    for obj in existing:
        merged[obj["objectId"]] = _stamp(obj)
    for obj in new_entries:
        merged[obj["objectId"]] = _stamp(obj)
        merged.move_to_end(obj["objectId"])
    while len(merged) > max_objects:
        merged.popitem(last=False)
    return list(merged.values())


def merge_lfu(existing: list[dict], new_entries: list[dict], max_objects: int) -> list[dict]:
    store: dict[str, dict] = {o["objectId"]: _stamp(o) for o in existing}
    for obj in new_entries:
        stamped = _stamp(obj)
        if obj["objectId"] in store:
            stamped["access_count"] = store[obj["objectId"]].get("access_count", 0) + 1
        store[obj["objectId"]] = stamped
    if len(store) <= max_objects:
        return list(store.values())
    ranked = sorted(store.values(), key=lambda x: (x.get("access_count", 0), x.get("timestamp", 0)))
    keep = ranked[-max_objects:]
    return keep


def merge_wtinylfu(existing: list[dict], new_entries: list[dict], max_objects: int) -> list[dict]:
    """Approximate W-TinyLFU: window (new) + main (LFU eviction)."""
    window_size = max(1, max_objects // 4)
    main_size = max_objects - window_size
    main = merge_lfu(existing, [], main_size)
    window = [_stamp(o) for o in new_entries]
    combined = merge_fifo(main, window, max_objects)
    if len(combined) > max_objects:
        combined = merge_lfu(combined, [], max_objects)
    return combined


def apply_replacement(
    existing: list[dict],
    new_entries: list[dict],
    *,
    policy: Policy = "fifo",
    max_objects: int = 100,
) -> list[dict]:
    if policy == "lfu":
        return merge_lfu(existing, new_entries, max_objects)
    if policy == "wtinylfu":
        return merge_wtinylfu(existing, new_entries, max_objects)
    return merge_fifo(existing, new_entries, max_objects)

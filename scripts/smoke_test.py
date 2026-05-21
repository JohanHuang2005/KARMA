#!/usr/bin/env python3
"""Non-GUI smoke tests for KARMA (no full task loop)."""
from __future__ import annotations

import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(__file__))

RESULTS: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))


def test_paths() -> None:
    from karma_paths import KARMA_ROOT, MEMORY_DIR, PROMPTS_DIR

    ok = KARMA_ROOT.is_dir() and (PROMPTS_DIR / "instruction.txt").exists()
    record("paths", ok, str(KARMA_ROOT))


def test_imports() -> None:
    try:
        import memory_save  # noqa: F401
        import mapping  # noqa: F401
        import longterm_save  # noqa: F401
        record("utility_imports", True)
    except Exception as e:
        record("utility_imports", False, str(e))


def test_memory_diff() -> None:
    from memory_save import compare_objects_location
    from karma_paths import MEMORY_DIR

    f1 = MEMORY_DIR / "objects_locations1.json"
    f2 = MEMORY_DIR / "objects_locations2.json"
    out = MEMORY_DIR / "memory3.json"
    if not f1.exists() or not f2.exists():
        record("memory_diff", False, "missing objects_locations json")
        return
    compare_objects_location(str(f1), str(f2), str(out))
    record("memory_diff", out.exists(), str(out))


def test_sentence_transformers() -> None:
    if os.environ.get("KARMA_SKIP_DOWNLOADS") == "1":
        record("sentence_transformers", True, "skipped (KARMA_SKIP_DOWNLOADS=1)")
        return
    try:
        os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
        from sentence_transformers import SentenceTransformer

        m = SentenceTransformer("all-mpnet-base-v2")
        emb = m.encode(["apple", "wash apple"], convert_to_tensor=False)
        record("sentence_transformers", len(emb) == 2, "model downloaded")
    except Exception as e:
        record("sentence_transformers", False, str(e)[:200])


def test_ai2thor() -> None:
    if os.environ.get("KARMA_SKIP_DOWNLOADS") == "1":
        record("ai2thor", True, "skipped (KARMA_SKIP_DOWNLOADS=1)")
        return
    try:
        from karma_paths import ensure_runtime_env

        ensure_runtime_env()
        from ai2thor.controller import Controller

        kwargs = dict(scene="FloorPlan1", width=300, height=300, quality="Low")
        try:
            from ai2thor.platform import CloudRendering

            kwargs["platform"] = CloudRendering
        except ImportError:
            pass

        c = Controller(**kwargs)
        ev = c.step(action="Pass")
        ok = ev.metadata is not None
        c.stop()
        record("ai2thor", ok, "FloorPlan1 loaded")
    except Exception as e:
        record("ai2thor", False, str(e)[:200])


def test_dashscope_key() -> None:
    try:
        from dashscope_client import get_api_key

        key = get_api_key()
        record("dashscope_api_key", bool(key and key.startswith("sk-")), "Bailian/DashScope")
    except Exception as e:
        record("dashscope_api_key", False, str(e)[:120])


def test_dashscope_chat() -> None:
    if os.environ.get("KARMA_SKIP_DOWNLOADS") == "1":
        record("dashscope_chat", True, "skipped (KARMA_SKIP_DOWNLOADS=1)")
        return
    try:
        from dashscope_client import chat_completion

        text = chat_completion(
            [{"role": "user", "content": "Reply with exactly: OK"}],
            max_tokens=16,
        )
        record("dashscope_chat", "OK" in text.upper(), text[:40])
    except Exception as e:
        record("dashscope_chat", False, str(e)[:120])


def main() -> int:
    os.environ.setdefault("KARMA_ROOT", str(__import__("pathlib").Path(__file__).resolve().parent.parent))

    if os.path.exists(os.path.join(os.path.dirname(__file__), "..", ".env")):
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

    print("=== KARMA smoke test ===\n")
    for fn in (
        test_paths,
        test_imports,
        test_memory_diff,
        test_sentence_transformers,
        test_ai2thor,
        test_dashscope_key,
        test_dashscope_chat,
    ):
        try:
            fn()
        except Exception:
            record(fn.__name__, False, traceback.format_exc().splitlines()[-1])

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    print(f"\n=== {passed}/{total} passed ===")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Non-GUI smoke tests for KARMA."""
from __future__ import annotations

import json
import os
import sys
import traceback

# Bootstrap: repo root is parent of scripts/
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RESULTS: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))


def test_paths() -> None:
    from src.paths import resolve

    ok = resolve("prompts/instruction.txt").exists()
    record("paths", ok, "prompts/instruction.txt")


def test_portable_cwd() -> None:
    """Run path resolution without relying on shell cwd."""
    from src.paths import ensure_repo_cwd, resolve

    original = os.getcwd()
    try:
        os.chdir("/tmp")
        ensure_repo_cwd()
        ok = resolve("memory/memory3.json").parent.exists()
        record("portable_cwd", ok, "resolved from /tmp")
    finally:
        os.chdir(original)


def test_imports() -> None:
    try:
        from src.memory import mapping, save, longterm  # noqa: F401
        from src.llm import client, planner  # noqa: F401
        record("package_imports", True)
    except Exception as e:
        record("package_imports", False, str(e))


def test_memory_diff() -> None:
    from src.memory.save import compare_objects_location
    from src.paths import resolve

    f1 = resolve("memory/objects_locations1.json")
    f2 = resolve("memory/objects_locations2.json")
    out = resolve("memory/memory3.json")
    if not f1.exists() or not f2.exists():
        record("memory_diff", False, "missing objects_locations json")
        return
    compare_objects_location(str(f1), str(f2), str(out))
    record("memory_diff", out.exists(), "memory/memory3.json")


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
        from src.paths import ensure_runtime_env

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
        from src.paths import load_dotenv
        from src.llm.client import get_api_key

        load_dotenv()
        key = get_api_key()
        record("dashscope_api_key", bool(key and key.startswith("sk-")), "Bailian/DashScope")
    except Exception as e:
        record("dashscope_api_key", False, str(e)[:120])


def test_dashscope_chat() -> None:
    if os.environ.get("KARMA_SKIP_DOWNLOADS") == "1":
        record("dashscope_chat", True, "skipped (KARMA_SKIP_DOWNLOADS=1)")
        return
    try:
        from src.llm.client import chat_completion

        text = chat_completion(
            [{"role": "user", "content": "Reply with exactly: OK"}],
            max_tokens=16,
        )
        record("dashscope_chat", "OK" in text.upper(), text[:40])
    except Exception as e:
        record("dashscope_chat", False, str(e)[:120])


def test_wandb_offline() -> None:
    try:
        import wandb
        from src.paths import ensure_repo_cwd, load_dotenv, resolve

        load_dotenv()
        ensure_repo_cwd()
        run = wandb.init(project="KARMA", mode="offline", job_type="smoke")
        wandb.log({"smoke_test": 1})
        run.finish()
        ok = any(resolve("wandb").glob("offline-run-*"))
        record("wandb_offline", ok, "offline run dir created")
    except Exception as e:
        record("wandb_offline", False, str(e)[:200])


def test_memory_replacement() -> None:
    from src.memory.replacement import apply_replacement

    out = apply_replacement([], [{"objectId": "x", "objectType": "Apple"}], policy="fifo", max_objects=2)
    record("memory_replacement", len(out) == 1, "fifo merge")


def test_ltm_graph() -> None:
    from src.memory.ltm_graph import serialize_graph_for_prompt

    graph = {
        "floor": {
            "name": "floor 1",
            "scene": "FloorPlan1",
            "areas": [
                {
                    "name": "node 1",
                    "type": "Area",
                    "position": [0, 0, 0],
                    "contains": ["Sink"],
                    "adjacent_nodes": [],
                    "objects": [],
                }
            ],
        }
    }
    text = serialize_graph_for_prompt(graph)
    record("ltm_graph", "adjacent nodes" in text and "Sink" in text)


def test_alfred_l_dataset() -> None:
    from src.benchmark.alfred_l import validate_alfred_l_dataset

    report = validate_alfred_l_dataset()
    record("alfred_l_dataset", report["valid"], f"{report['total_tasks']} tasks")


def test_stm_retrieval_local() -> None:
    from config import Config
    from src.memory.retrieval import run_memory_retrieval
    from src.paths import resolve

    cfg = Config()
    cfg.memory.embedding_backend = "local"
    cfg.memory.similarity_threshold = 0.0
    resolve("memory/analysis_results.json").write_text("{}", encoding="utf-8")
    resolve("memory/memory3.json").write_text(
        json.dumps(
            [
                {
                    "objectId": "Apple|1",
                    "objectType": "Apple",
                    "position": {"x": 1.0, "y": 0.9, "z": 2.0},
                    "state": "cleaned",
                }
            ]
        ),
        encoding="utf-8",
    )
    resolve("prompts/instruction.txt").write_text(
        "Please help me decompose: wash an apple.", encoding="utf-8"
    )
    metrics = run_memory_retrieval(cfg)
    ok = metrics.get("stm_used") and resolve("prompts/short_term_memory.txt").read_text().strip()
    record("stm_retrieval_local", bool(ok), f"score={metrics.get('best_similarity', 0):.2f}")


def main() -> int:
    from src.paths import load_dotenv

    load_dotenv()

    print("=== KARMA smoke test ===\n")
    for fn in (
        test_paths,
        test_portable_cwd,
        test_imports,
        test_memory_diff,
        test_memory_replacement,
        test_ltm_graph,
        test_alfred_l_dataset,
        test_stm_retrieval_local,
        test_sentence_transformers,
        test_ai2thor,
        test_dashscope_key,
        test_dashscope_chat,
        test_wandb_offline,
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

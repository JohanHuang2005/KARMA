# KARMA: Paper vs Code — Discrepancy & Refactor Status

Comparison baseline:

- **Paper:** Wang et al., *KARMA* (arXiv:2409.14908)
- **Official prototype:** [WZX0Swarm0Robotics/KARMA `master`](https://github.com/WZX0Swarm0Robotics/KARMA/tree/master)
- **Our branch:** `refactor` on [JohanHuang2005/KARMA](https://github.com/JohanHuang2005/KARMA)

Last updated: **2026-05-21** (paper-alignment pass on `refactor`).

---

## Legend

| Status | Meaning |
|--------|---------|
| ✅ Fixed on `refactor` | Implemented to match paper (or documented acceptable substitute) |
| 🟡 Partial | Core mechanism present; full paper fidelity still blocked |
| ❌ Open | Not implemented; paper claims remain unreproducible from code |

---

## 1. Repository & reproducibility

| Topic | Official code | `refactor` status |
|--------|---------------|-------------------|
| Hard-coded `/home/user/wzx/karma/` | ❌ | ✅ `src/paths.py` repo-relative paths |
| Missing `api_key` in executor | ❌ | ✅ unified `src/llm/client.py` |
| Import-time side effects | ❌ | ✅ planner/executor invoked via `pipeline.py` only |
| `main` vs `master` confusion | ❌ | 🟡 README warns to clone `master` / use our fork |
| Supplementary material | ❌ | ❌ still absent |
| Real-robot deployment | ❌ | ❌ still absent |

---

## 2. Long-term memory (LTM) — Sec. IV-A

| Paper claim | Official | `refactor` |
|-------------|----------|------------|
| 3DSG floor → area → object | Partial grid only | ✅ `src/memory/ltm_graph.py`: floor + area nodes + static objects |
| Navigability edges between areas | ❌ | ✅ adjacency from reachable-position regions |
| Serialize `{name, type, contains, adjacent nodes, position}` | ❌ static txt | ✅ auto-writes `prompts/long_term_memory.txt` + `memory/ltm_scene_graph.json` |
| Update when environment changes | ❌ | 🟡 rebuilt at sim init (`save_ltm_from_controller`); not incremental mid-episode |
| Faster R-CNN on real robot | N/A in sim | ❌ AI2-THOR metadata only |

**Files:** `src/memory/ltm_graph.py`, `src/memory/longterm.py`, `src/env/executor.py` (init).

---

## 3. Short-term memory (STM) — Sec. IV-B

| Paper claim | Official | `refactor` |
|-------------|----------|------------|
| VLM extracts object state after image | Put + GPT-4o | ✅ Put + vision model via `analyze_image_with_task` |
| Unit = coords + state + image | image not in unit | ✅ `memory3.json` entries include `image`, `state`, `position` |
| Embedding-based recall | MPNet on `objectType`, top-1 | ✅ `src/memory/embeddings.py` + `retrieval.py`; **top-K** (`memory.stm_top_k`, default **1** per Sec. IV-C) |
| Unified STM gating | lexical + embedding split | ✅ embedding similarity → `logs/similarity_flag.json` |
| Default embedding model | text-embedding-3-large | ✅ config default; **local MPNet fallback** when API unavailable |

**Files:** `src/memory/save.py`, `src/memory/retrieval.py`, `src/memory/embeddings.py`.

---

## 4. Planner & LLM — Sec. IV-C, V-A

| Paper claim | Official | `refactor` |
|-------------|----------|------------|
| Planner GPT-4o | gpt-4o-mini | ✅ default `gpt-4o` in `config/config.py`; override via `DASHSCOPE_CHAT_MODEL` |
| Vision GPT-4o | gpt-4o | ✅ default `gpt-4o`; override via `DASHSCOPE_VISION_MODEL` |
| Experience RAG top-3 | 4 examples | ✅ unchanged count; retrieval uses paper embedding path |
| Clean pipeline | import-time API | ✅ `src/pipeline.py` orchestrates retrieval → planner → executor |
| `GoToObject_with_memory` in plans | unused | 🟡 prompts updated (`prompts/emphasize.txt`); LLM may still prefer `Explore` |

---

## 5. Memory replacement — Sec. IV-D

| Paper claim | Official | `refactor` |
|-------------|----------|------------|
| FIFO + merge by objectId | broken timestamp sort | ✅ `src/memory/replacement.py` (`fifo`) |
| LFU | ❌ | ✅ `policy="lfu"` |
| W-TinyLFU | ❌ | 🟡 approximate `policy="wtinylfu"` |
| ALFWorld-R + MHR metric | ❌ | ❌ not implemented |
| Configurable policy | ❌ | ✅ `memory.replacement_policy`, `memory.max_stm_objects` |

---

## 6. Evaluation — Sec. V–VI

| Paper claim | Official | `refactor` |
|-------------|----------|------------|
| ALFRED-L 48 tasks | JSON only | ✅ `src/benchmark/alfred_l.py` loader + manifest (`--benchmark.task_name alfred_l`) |
| SR / MRA / RE / RT metrics | ❌ | ❌ manifest/validation only; no full goal-check loop |
| Baselines (CAPEAM, HELPER, LoTa-Bench) | ❌ | ❌ |
| `long_task_1`–`6` | missing `long_task_5` | ✅ `long_task_5` added in `src/benchmark/eval.py` |
| LLM pipeline on ALFRED-L | decoupled | 🟡 dataset wired; end-to-end eval still manual |

**Commands:**

```bash
# Validate ALFRED-L manifest (dry run)
python main.py benchmark --benchmark.task_name alfred_l

# Hand-written long-horizon tasks
python main.py benchmark --benchmark.task_name long_task_5
```

---

## 7. Executor & skills — Sec. IV-C

| Issue | Official | `refactor` |
|-------|----------|------------|
| Missing Open/Close/Slice/Clean/Break handlers | ❌ | ✅ `src/env/executor.py` `exec_actions` |
| Broken top-view screenshot | wrong variable | ✅ fixed (uses `top_view_rgb`) |
| Multi FloorPlan ALFRED-L | FloorPlan1 only | 🟡 ALFRED-L lists many plans; executor still defaults to FloorPlan1 |

---

## 8. Testing

| Test | Purpose |
|------|---------|
| `python scripts/test_paper_alignment.py` | FIFO, LTM serialization, ALFRED-L counts |
| `KARMA_SKIP_DOWNLOADS=1 python main.py smoke` | full smoke incl. STM local retrieval |
| `bash scripts/test_readme_commands.sh` | README regression |

---

## 9. Remaining gaps (honest scope)

These paper elements are **still not fully reproduced** on `refactor`:

1. **Table I numbers** — need goal-condition checker + multi-scene runner + baselines.
2. **ALFWorld-R** and **MHR** ablation for replacement policies.
3. **Multimodal embeddings** over (text + image) STM units — we embed structured text; images stored but not embedded jointly.
4. **Incremental LTM updates** during long episodes across environment changes.
5. **Real-robot stack** (Faster R-CNN, grasping, mobile base).
6. **Supplementary experiment details** not in public repo.

Use DashScope/Qwen in `.env` for day-to-day runs; set `DASHSCOPE_*=gpt-4o` and `KARMA_EMBEDDING_MODEL=text-embedding-3-large` when testing paper-faithful API settings.

---

## References

- Paper: arXiv:2409.14908
- Official code: https://github.com/WZX0Swarm0Robotics/KARMA/tree/master
- Refactor fork: https://github.com/JohanHuang2005/KARMA/tree/refactor

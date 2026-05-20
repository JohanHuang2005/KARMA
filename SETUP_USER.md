# KARMA — What you must provide externally

The repo environment (`.venv`, paths, scripts) is configured under `/root/project/KARMA`.
**Three assets cannot be bundled** and must be supplied by you (download or API key).

## 1. Alibaba Bailian / DashScope API key (required for full pipeline)

Used by `scripts/dashscope_client.py` (model **qwen3.5-omni-flash**):
- `scripts/llm_as_planner.py` — task code generation
- `scripts/execute_LLM_plan.py` — vision for short-term object **state**

```bash
cd /root/project/KARMA
cp .env.example .env
# Edit .env:
#   DASHSCOPE_API_KEY=sk-...
#   DASHSCOPE_CHAT_MODEL=qwen3.5-omni-flash
source .env
```

Without this key, **memory retrieval + STM scripts can run**, but **planning and vision analysis will fail**.

---

## 2. AI2-THOR CloudRendering build (~797 MB, first run)

On first `Controller(...)` with `CloudRendering`, ai2thor downloads:

`thor-CloudRendering-*.zip` (~797 MB)

- **You need:** stable network (or pre-download and place in ai2thor cache).
- Cache dir (typical): `~/.ai2thor/releases/` or path shown in download logs.

**Verify after download:**

```bash
source /root/project/KARMA/.venv/bin/activate
export KARMA_ROOT=/root/project/KARMA PYTHONPATH=$KARMA_ROOT/scripts
python -c "from ai2thor.controller import Controller; from ai2thor.platform import CloudRendering; c=Controller(scene='FloorPlan1', width=300, height=300, platform=CloudRendering); c.step('Pass'); c.stop(); print('ai2thor OK')"
```

On a machine **with a display**, you can also use the legacy local Unity build (no CloudRendering zip); this server uses headless CloudRendering.

---

## 3. Sentence-Transformers model `all-mpnet-base-v2` (~420 MB, Hugging Face)

Used by `scripts/query_with_short_term_memory.py` for STM / experience retrieval.

**Download (if huggingface.co is slow, use mirror):**

```bash
export HF_ENDPOINT=https://hf-mirror.com   # China mirror, optional
source /root/project/KARMA/.venv/bin/activate
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-mpnet-base-v2')"
```

Cache: `~/.cache/huggingface/` or `~/.cache/torch/sentence_transformers/`

---

## Optional (not required for core loop)

| Item | Purpose |
|------|---------|
| `ffmpeg` | Episode video export in `execute_LLM_plan.py` |
| X11 / VNC display | `cv2.imshow` in GUI / live viewer (headless runs can patch to disable) |
| Conda `environment.yml` | Original author env; we use `requirements.txt` + `.venv` instead |

---

## Quick start (after items 1–3)

```bash
cd /root/project/KARMA
bash scripts/setup_env.sh          # once: creates .venv
source .venv/bin/activate
export KARMA_ROOT=$PWD PYTHONPATH=$PWD/scripts
source .env                        # OPENAI_API_KEY

# Component checks (no GUI):
python scripts/smoke_test.py

# Full interactive flow (needs display for Tk + OpenCV windows):
python scripts/GUI_karma.py
```

---

## Already configured in this workspace

- [x] Python `.venv` + `requirements.txt` (CPU PyTorch)
- [x] Hardcoded `/home/user/wzx/karma` paths → `/root/project/KARMA`
- [x] `scripts/karma_paths.py`, `scripts/setup_env.sh`, `scripts/smoke_test.py`
- [x] `memory/short_term/` directory
- [x] `llm_as_planner.py` / `query_with_short_term_memory.py` — no longer run destructive code on import

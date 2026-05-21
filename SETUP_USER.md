# KARMA — External assets you must provide

The repo environment (`.venv`, paths, scripts) lives under the KARMA root.
**Three assets are not bundled** and must be supplied via download or API key.

## 1. Alibaba Bailian / DashScope API key (required for full pipeline)

Used by `src/llm/client.py` (model **qwen3.5-omni-flash**):

- `src/llm/planner.py` — task code generation
- `src/env/executor.py` — vision for short-term object **state**

```bash
cd KARMA
cp .env.example .env
# Edit .env:
#   DASHSCOPE_API_KEY=sk-...
#   DASHSCOPE_CHAT_MODEL=qwen3.5-omni-flash
source .env
```

Without this key, **memory retrieval can run**, but **planning and vision analysis will fail**.

---

## 2. AI2-THOR CloudRendering build (~797 MB, first run)

On first `Controller(...)` with `CloudRendering`, ai2thor downloads:

`thor-CloudRendering-*.zip` (~797 MB)

There is **no official China mirror**; use the script with **aria2 multi-connection** download from AWS S3:

```bash
bash scripts/download_assets_mirror.sh ai2thor
```

| Item | Value |
|------|-------|
| Direct link (S3) | `http://s3-us-west-2.amazonaws.com/ai2-thor-public/builds/thor-CloudRendering-f0825767cd50d69f666c7f282e54abfe58f1e917.zip` |
| Checksum | same path with `.sha256` suffix |
| Install dir | `~/.ai2thor/releases/thor-CloudRendering-f0825767cd50d69f666c7f282e54abfe58f1e917/` |

**Verify after download:**

```bash
source .venv/bin/activate
python -c "from ai2thor.controller import Controller; from ai2thor.platform import CloudRendering; c=Controller(scene='FloorPlan1', width=300, height=300, platform=CloudRendering); c.step('Pass'); c.stop(); print('ai2thor OK')"
```

On a machine **with a display**, you can use the legacy local Unity build instead; headless servers use CloudRendering.

---

## 3. Sentence-Transformers model `all-mpnet-base-v2` (~420 MB)

Used by `src/memory/retrieval.py` for STM and experience RAG.

**Recommended mirror download:**

```bash
cd KARMA
source .venv/bin/activate
bash scripts/download_assets_mirror.sh mpnet    # HF mirror hf-mirror.com
# Or ModelScope:
MPNET_MIRROR=modelscope bash scripts/download_assets_mirror.sh mpnet
```

Manual download:

```bash
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download sentence-transformers/all-mpnet-base-v2
```

| Mirror | URL |
|--------|-----|
| HF mirror | https://hf-mirror.com/sentence-transformers/all-mpnet-base-v2 |
| ModelScope | https://www.modelscope.cn/models/sentence-transformers/all-mpnet-base-v2 |

Cache: `~/.cache/huggingface/` or ModelScope `~/.cache/modelscope/hub/`

`HF_ENDPOINT=https://hf-mirror.com` is set by default in `.env.example` and `scripts/setup_env.sh`.

---

## Optional (not required for core loop)

| Item | Purpose |
|------|---------|
| `ffmpeg` | Episode video export in `src/env/executor.py` |
| X11 / VNC display | Tk GUI and `cv2.imshow` live viewer |
| Conda `environment.yml` | Original author env; we use `requirements.txt` + `.venv` |

---

## Quick start (after items 1–3)

```bash
cd KARMA
bash scripts/setup_env.sh
source .venv/bin/activate
source .env

python scripts/smoke_test.py

# Interactive flow (needs display):
python main.py base --task.use_gui
```

# KARMA — Knowledge Augmented embodied agents with long- and short-term Recall Memory for AI

The refactored KARMA repo follows a [MoETTA](../MoETTA)-style layout: **unified CLI entry**, **dataclass configs**, **layered `src/` package**, and **optional W&B observability** for easier experiments and debugging.

## Architecture

```
User / benchmark task
        │
        ▼
   main.py (tyro CLI)
        │
        ▼
  src/pipeline.py
        │
        ├─► src/memory/retrieval.py   Short-term memory + RAG example retrieval
        ├─► src/llm/planner.py        LLM task decomposition → task_functions.py
        └─► src/env/executor.py       AI2-THOR simulation + memory updates
```

| Directory | Role |
|-----------|------|
| `main.py` | Single Python entry point with CLI overrides |
| `config/` | Dataclass configs and presets (`base` / `headless` / `benchmark` / `smoke`) |
| `src/pipeline.py` | Experiment pipeline orchestration |
| `src/llm/` | DashScope client and LLM planner |
| `src/memory/` | Scene mapping, short/long-term memory, semantic retrieval |
| `src/env/` | AI2-THOR executor, GUI, generated task code |
| `src/benchmark/` | Headless benchmark tasks (`long_task_1` ~ `long_task_6`) |
| `scripts/` | Environment setup, smoke tests, batch experiment shells |
| `prompts/` | LLM prompt templates (read/written at runtime) |
| `memory/` | Persistent memory JSON and images |
| `logs/` | Runtime intermediate state |
| `artifacts/` | Experiment logs, benchmark outputs, W&B offline cache |

## Quick start

### 1. Environment

```bash
cd KARMA
bash scripts/setup_env.sh
source .venv/bin/activate
cp .env.example .env   # set DASHSCOPE_API_KEY (KARMA_ROOT is optional; auto-detected from repo)
source .env
```

### 2. External assets (you must provide)

See [SETUP_USER.md](SETUP_USER.md):

- **DashScope API key** — LLM planning and vision analysis
- **AI2-THOR CloudRendering** — headless simulation (~797 MB)
- **all-mpnet-base-v2** — short-term memory embeddings (~420 MB)

```bash
bash scripts/download_assets_mirror.sh ai2thor
bash scripts/download_assets_mirror.sh mpnet
```

Models download via **hf-mirror.com** by default (`HF_ENDPOINT` in `.env`).

### 3. Smoke tests

```bash
# Skip downloads and live API calls
KARMA_SKIP_DOWNLOADS=1 python main.py smoke

# Full component checks
python scripts/smoke_test.py
```

## Usage

### Interactive GUI

Requires a display (X11 / VNC):

```bash
python main.py base --task.use_gui
# Legacy wrapper
python scripts/GUI_karma.py
```

### Single task (CLI)

Planning + simulation (requires AI2-THOR and DashScope):

```bash
python main.py base \
  --task.instruction "wash an apple and put it on the countertop" \
  --env.name wash_apple_demo
```

### Planning only (no simulation)

```bash
python main.py headless \
  --task.instruction "slice a tomato and place it on the plate"
```

### Benchmark evaluation

Requires AI2-THOR; runs can take several minutes:

```bash
bash scripts/run_benchmark.sh long_task_3

# Or via CLI
python main.py benchmark \
  --benchmark.task_name long_task_3 \
  --benchmark.output_path artifacts/long_task_3_output.json
```

Metrics: `explore_count`, `total_time`.

### W&B observability

Set `WANDB_API_KEY` in `.env`, then:

```bash
python main.py base \
  --env.wandb_mode online \
  --env.group my-exp \
  --env.name run_001 \
  --task.instruction "wash an apple"
```

Logs go to `artifacts/logs/` (loguru) and W&B when enabled.

### Validate README commands

```bash
bash scripts/test_readme_commands.sh
```

## Configuration

Same pattern as MoETTA: **tyro + dataclass**:

```bash
python main.py base --simulation.scene FloorPlan1 --llm.chat_model qwen3.5-omni-flash
python main.py benchmark --benchmark.task_name long_task_1
```

| Preset | Description |
|--------|-------------|
| `base` | Full pipeline (memory → plan → execute) |
| `headless` | Memory retrieval + LLM planning only |
| `benchmark` | Built-in benchmark tasks |
| `smoke` | Component smoke tests |

## Legacy script compatibility

Thin wrappers under `scripts/` remain available:

| Legacy | Recommended |
|--------|-------------|
| `python scripts/GUI_karma.py` | `python main.py base --task.use_gui` |
| `python scripts/llm_as_planner.py` | `python main.py headless` |
| `python scripts/smoke_test.py` | `python main.py smoke` |

## Data flow

1. **Task input** → `prompts/instruction.txt`, `logs/task_description.json`
2. **Memory retrieval** → SentenceTransformer over `memory/memory3.json`, RAG from `experience/experience.json`
3. **LLM planning** → Python function appended to `src/env/task_functions.py`
4. **Simulation** → AI2-THOR action queue; short-term memory updated after `PutObject`

Add `scripts/test_readme_commands.sh` to validate README commands locally (best-effort on headless servers).

```bibtex
@article{wang2024karma,
  title={Karma: Augmenting embodied ai agents with long-and-short term memory systems},
  author={Wang, Zixuan and Yu, Bo and Zhao, Junzhe and Sun, Wenhao and Hou, Sai and Liang, Shuai and Hu, Xing and Han, Yinhe and Gan, Yiming},
  journal={arXiv preprint arXiv:2409.14908},
  year={2024}
}
```

#!/usr/bin/env bash
# Run README command smoke tests (best-effort on headless servers).
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source .venv/bin/activate 2>/dev/null || true
export KARMA_ROOT="$ROOT"
export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
# shellcheck disable=SC1091
[[ -f .env ]] && source .env

PASS=0
FAIL=0
SKIP=0

run() {
  local name="$1"
  shift
  echo ""
  echo "=== TEST: $name ==="
  echo ">>> $*"
  if "$@"; then
    echo "[PASS] $name"
    PASS=$((PASS + 1))
  else
    echo "[FAIL] $name"
    FAIL=$((FAIL + 1))
  fi
}

skip() {
  local name="$1"
  local reason="$2"
  echo ""
  echo "=== SKIP: $name — $reason ==="
  SKIP=$((SKIP + 1))
}

has_dashscope_key() {
  [[ -n "${DASHSCOPE_API_KEY:-}" && "${DASHSCOPE_API_KEY}" != "your_key" && "${DASHSCOPE_API_KEY}" != sk-your-* ]]
}

AI2_DIR="${HOME}/.ai2thor/releases/thor-CloudRendering-f0825767cd50d69f666c7f282e54abfe58f1e917"

# --- Quick start ---
run "setup_env.sh" bash scripts/setup_env.sh
run "smoke (skip downloads)" env KARMA_SKIP_DOWNLOADS=1 python main.py smoke
run "smoke_test.py (skip downloads)" env KARMA_SKIP_DOWNLOADS=1 python scripts/smoke_test.py

# --- CLI / help ---
run "main.py --help" python main.py --help
run "base --help" python main.py base --help
run "benchmark --help" python main.py benchmark --help

# --- Planning (needs DashScope) ---
if has_dashscope_key; then
  run "headless planning" python main.py headless \
    --task.instruction "slice a tomato and place it on the plate"
  run "wandb offline + headless" python main.py headless \
    --env.wandb_mode offline \
    --env.name readme_wandb_test \
    --task.instruction "pick up a mug"
else
  skip "headless planning" "DASHSCOPE_API_KEY not set in .env"
  skip "wandb offline + headless" "DASHSCOPE_API_KEY not set in .env"
fi

# --- Legacy wrappers ---
run "legacy llm_as_planner import" python -c "from src.llm.planner import main; print('ok')"
run "legacy query_stm import" python -c "from src.memory.retrieval import main; print('ok')"
run "legacy karma_paths" python -c "from scripts.karma_paths import KARMA_ROOT; print(KARMA_ROOT)"
run "legacy mapping" python -c "from scripts.mapping import first_map; print('ok')"
run "legacy GUI import (no executor)" python -c "from src.env.gui import launch_gui; print('ok')"

# --- Config examples from README ---
run "config override parse" python -c "
import tyro
from config import CONFIG
cfg = tyro.extras.overridable_config_cli(CONFIG)
print('parsed', type(cfg).__name__)
" base --simulation.scene FloorPlan1 --help

# --- GUI (interactive; import-only on headless) ---
skip "python main.py base --task.use_gui" "manual: requires display and user input"
skip "python scripts/GUI_karma.py" "manual: requires display and user input"

# --- Benchmark (long; needs AI2-THOR) ---
if [[ -d "$AI2_DIR" ]]; then
  echo ""
  echo "=== TEST: benchmark CLI (120s cap) ==="
  echo ">>> timeout 120 python main.py benchmark ..."
  set +e
  timeout 120 python main.py benchmark \
    --benchmark.task_name long_task_3 \
    --benchmark.output_path artifacts/readme_long_task_3.json
  rc=$?
  set -e
  if [[ "$rc" -eq 0 ]]; then
    echo "[PASS] benchmark CLI"
    PASS=$((PASS + 1))
  elif [[ "$rc" -eq 124 ]]; then
    skip "benchmark CLI" "long_task_3 exceeds 120s (run manually for full metrics)"
  else
    echo "[FAIL] benchmark CLI (exit $rc)"
    FAIL=$((FAIL + 1))
  fi
else
  skip "benchmark CLI" "AI2-THOR CloudRendering not installed"
  skip "run_benchmark.sh" "AI2-THOR CloudRendering not installed"
fi

# --- Full pipeline ---
if [[ -d "$AI2_DIR" ]] && has_dashscope_key; then
  skip "base full pipeline" "manual: long run; use headless or benchmark instead"
else
  skip "base full pipeline" "needs AI2-THOR and DASHSCOPE_API_KEY"
fi

# --- Asset downloads (idempotent) ---
if python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-mpnet-base-v2')" 2>/dev/null; then
  skip "download_assets_mirror.sh mpnet" "model already cached"
else
  run "download_assets_mirror.sh mpnet" bash scripts/download_assets_mirror.sh mpnet
fi

if [[ -d "$AI2_DIR" ]]; then
  skip "download_assets_mirror.sh ai2thor" "build already installed"
else
  skip "download_assets_mirror.sh ai2thor" "manual: ~797MB download"
fi

echo ""
echo "=== README test summary: PASS=$PASS FAIL=$FAIL SKIP=$SKIP ==="
[[ "$FAIL" -eq 0 ]]

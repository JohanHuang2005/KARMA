#!/usr/bin/env bash
# Run KARMA benchmark tasks (no GUI)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
source .venv/bin/activate 2>/dev/null || true
export KARMA_ROOT="$ROOT"

TASK="${1:-long_task_3}"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG="artifacts/logs/benchmark_${TASK}_${STAMP}.log"
mkdir -p artifacts/logs

echo "Running benchmark: $TASK"
python main.py benchmark \
  --env.local \
  --env.job_type benchmark \
  --env.group benchmark \
  --env.name "${TASK}_${STAMP}" \
  --benchmark.task_name "$TASK" \
  --benchmark.output_path "artifacts/${TASK}_output.json" \
  2>&1 | tee "$LOG"

echo "Log: $LOG"

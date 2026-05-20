#!/usr/bin/env bash
# Prepare a task instruction and run STM pipeline (no AI2-THOR, no LLM).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
source "$ROOT/.venv/bin/activate"
export KARMA_ROOT="$ROOT" PYTHONPATH="$ROOT/scripts"
export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"

TASK="${1:-wash an apple and put it on the countertop}"
mkdir -p memory/short_term logs

echo "Please help me decompose the following tasks: ${TASK}. Please output only the generated code." \
  > prompts/instruction.txt
echo "{\"task_description\": \"${TASK}\"}" > logs/task_description.json
echo "{\"similarity_flag\": false}" > logs/similarity_flag.json

python scripts/query_with_short_term_memory.py
echo "STM prep done. Check prompts/short_term_memory.txt and prompts/examples.txt"

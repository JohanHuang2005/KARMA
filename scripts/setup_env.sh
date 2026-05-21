#!/usr/bin/env bash
# One-time environment setup for KARMA (current repo layout).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export KARMA_ROOT="$ROOT"
export PYTHONPATH="${ROOT}/scripts:${PYTHONPATH:-}"
export VK_ICD_FILENAMES="${VK_ICD_FILENAMES:-/etc/vulkan/icd.d/nvidia_icd.json}"

VENV="${ROOT}/.venv"
if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"

pip install -U pip wheel
pip install -r requirements.txt

mkdir -p memory/short_term logs history_tasks

if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

echo "KARMA env ready."
echo "  KARMA_ROOT=$KARMA_ROOT"
echo "  Python: $(which python)"
echo "  DASHSCOPE_API_KEY: ${DASHSCOPE_API_KEY:+set}${DASHSCOPE_API_KEY:-NOT SET}"
echo "  Model: ${DASHSCOPE_CHAT_MODEL:-qwen3.5-omni-flash}"

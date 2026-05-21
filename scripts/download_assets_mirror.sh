#!/usr/bin/env bash
# Download KARMA external assets via China-friendly mirrors / accelerated tools.
#
# 1) all-mpnet-base-v2  — HF 镜像 (hf-mirror) 或 ModelScope 魔搭
# 2) AI2-THOR CloudRendering — 无官方国内镜像；使用 aria2 多线程从 S3 加速拉取并解压
#
# Usage:
#   bash scripts/download_assets_mirror.sh          # both
#   bash scripts/download_assets_mirror.sh mpnet    # STM model only
#   bash scripts/download_assets_mirror.sh ai2thor  # simulator only
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
[[ -f "$ROOT/.venv/bin/activate" ]] && source "$ROOT/.venv/bin/activate"
export KARMA_ROOT="$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"

MPNET_BACKEND="${MPNET_MIRROR:-hf}"   # hf | modelscope
AI2_COMMIT="f0825767cd50d69f666c7f282e54abfe58f1e917"
AI2_NAME="thor-CloudRendering-${AI2_COMMIT}"
AI2_URL="http://s3-us-west-2.amazonaws.com/ai2-thor-public/builds/${AI2_NAME}.zip"
AI2_SHA_URL="${AI2_URL%.zip}.sha256"
AI2_RELEASES="${HOME}/.ai2thor/releases"
AI2_TMP="${HOME}/.ai2thor/tmp"
AI2_ZIP="${AI2_TMP}/${AI2_NAME}.zip"

log() { echo "[download] $*"; }

download_mpnet_hf_mirror() {
  log "=== [1/2] all-mpnet-base-v2 via HF 镜像 (hf-mirror.com) ==="
  export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
  export HF_HUB_DISABLE_XET="${HF_HUB_DISABLE_XET:-1}"
  log "HF_ENDPOINT=$HF_ENDPOINT  HF_HUB_DISABLE_XET=$HF_HUB_DISABLE_XET"
  find "${HOME}/.cache/huggingface/hub/.locks" -name "*.lock" -delete 2>/dev/null || true
  python -c "
import os
os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
os.environ.setdefault('HF_HUB_DISABLE_XET', '1')
from huggingface_hub import snapshot_download
path = snapshot_download(
    'sentence-transformers/all-mpnet-base-v2',
    allow_patterns=[
        'config.json', 'model.safetensors', 'tokenizer*', 'vocab.txt',
        'modules.json', '1_Pooling/*', 'sentence_bert_config.json',
        'special_tokens_map.json', 'config_sentence_transformers.json',
    ],
)
print('HF mirror cache:', path)
from sentence_transformers import SentenceTransformer
m = SentenceTransformer('all-mpnet-base-v2')
print('sentence-transformers OK, dim=', m.get_sentence_embedding_dimension())
"
}

download_mpnet_modelscope() {
  log "=== [1/2] all-mpnet-base-v2 via ModelScope 魔搭 (需 Python>=3.9) ==="
  pyver="$(python -c 'import sys; print(sys.version_info[:2])')"
  log "Python $pyver"
  pip install -q "modelscope>=1.15" 2>/dev/null || pip install modelscope
  python -c "
from modelscope import snapshot_download
path = snapshot_download('sentence-transformers/all-mpnet-base-v2')
print('ModelScope path:', path)
from sentence_transformers import SentenceTransformer
m = SentenceTransformer('all-mpnet-base-v2')
print('sentence-transformers OK, dim=', m.get_sentence_embedding_dimension())
"
}

download_ai2thor_build() {
  log "=== [2/2] AI2-THOR CloudRendering (~797MB, aria2 多线程) ==="
  if [[ -d "${AI2_RELEASES}/${AI2_NAME}" ]]; then
    log "Already installed: ${AI2_RELEASES}/${AI2_NAME}"
    return 0
  fi
  mkdir -p "$AI2_TMP" "$AI2_RELEASES"
  log "Fetching SHA256..."
  local expected_sha
  expected_sha="$(curl -fsSL --max-time 60 "$AI2_SHA_URL" | tr -d '[:space:]')"
  log "Expected SHA256: ${expected_sha:0:16}..."

  if [[ -f "$AI2_ZIP" ]]; then
    local actual_sha
    actual_sha="$(sha256sum "$AI2_ZIP" | awk '{print $1}')"
    if [[ "$actual_sha" == "$expected_sha" ]]; then
      log "Zip already present and checksum OK: $AI2_ZIP"
    else
      log "Removing incomplete/wrong zip (checksum mismatch)"
      rm -f "$AI2_ZIP"
    fi
  fi

  if [[ ! -f "$AI2_ZIP" ]]; then
    log "Downloading (no official CN mirror — using aria2 multi-connection from AWS S3)"
    log "URL: $AI2_URL"
    if command -v aria2c &>/dev/null; then
      aria2c -x 16 -s 16 -k 1M --continue=true -d "$(dirname "$AI2_ZIP")" -o "$(basename "$AI2_ZIP")" "$AI2_URL"
    else
      wget -c -O "$AI2_ZIP" "$AI2_URL"
    fi
  fi

  actual_sha="$(sha256sum "$AI2_ZIP" | awk '{print $1}')"
  if [[ "$actual_sha" != "$expected_sha" ]]; then
    echo "ERROR: SHA256 mismatch for $AI2_ZIP" >&2
    echo "  expected: $expected_sha" >&2
    echo "  actual:   $actual_sha" >&2
    exit 1
  fi
  log "Checksum OK. Extracting to ${AI2_RELEASES}/${AI2_NAME} ..."

  python <<PY
import os, zipfile, shutil

releases_dir = os.path.expanduser("${AI2_RELEASES}")
tmp_dir = os.path.expanduser("${AI2_TMP}")
name = "${AI2_NAME}"
zip_path = os.path.expanduser("${AI2_ZIP}")
base_dir = os.path.join(releases_dir, name)
extract_dir = os.path.join(tmp_dir, name + "_extract")

if os.path.isdir(base_dir):
    print("Already extracted:", base_dir)
else:
    if os.path.isdir(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(extract_dir)
    if os.path.isdir(base_dir):
        shutil.rmtree(base_dir)
    os.rename(extract_dir, base_dir)
    exe = os.path.join(base_dir, name)
    if os.path.isfile(exe):
        os.chmod(exe, 0o755)
    print("Extracted:", base_dir)
PY

  python -c "
import os
from karma_paths import ensure_runtime_env
ensure_runtime_env()
from ai2thor.controller import Controller
from ai2thor.platform import CloudRendering
c = Controller(scene='FloorPlan1', width=300, height=300, quality='Low', platform=CloudRendering)
c.step(action='Pass')
c.stop()
print('AI2-THOR smoke test OK')
"
}

TARGET="${1:-all}"
case "$TARGET" in
  mpnet|model)
    if [[ "$MPNET_BACKEND" == "modelscope" ]]; then
      download_mpnet_modelscope
    else
      download_mpnet_hf_mirror
    fi
    ;;
  ai2thor|thor)
    download_ai2thor_build
    ;;
  all|"")
    if [[ "$MPNET_BACKEND" == "modelscope" ]]; then
      download_mpnet_modelscope
    else
      download_mpnet_hf_mirror
    fi
    download_ai2thor_build
    ;;
  *)
    echo "Usage: $0 [all|mpnet|ai2thor]" >&2
    echo "  MPNET_MIRROR=hf|modelscope  (default: hf)" >&2
    exit 1
    ;;
esac

log "=== All requested downloads finished ==="

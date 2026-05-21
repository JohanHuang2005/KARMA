"""Alibaba Cloud Bailian (DashScope) OpenAI-compatible client for Qwen models."""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests

# Beijing region DashScope compatible-mode endpoint
DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_CHAT_MODEL = "qwen3.5-omni-flash"
DEFAULT_VISION_MODEL = "qwen3.5-omni-flash"


def _load_dotenv() -> None:
    from src.paths import KARMA_ROOT

    env_file = KARMA_ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()


def get_api_key() -> str:
    key = (
        os.environ.get("DASHSCOPE_API_KEY")
        or os.environ.get("BAILIAN_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or ""
    )
    if not key or key == "your_key":
        raise RuntimeError(
            "Set DASHSCOPE_API_KEY in .env (see .env.example). "
            "Get key from https://bailian.console.aliyun.com/"
        )
    return key


def get_base_url() -> str:
    return os.environ.get("DASHSCOPE_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def get_chat_model() -> str:
    return os.environ.get("DASHSCOPE_CHAT_MODEL", DEFAULT_CHAT_MODEL)


def get_vision_model() -> str:
    return os.environ.get("DASHSCOPE_VISION_MODEL", DEFAULT_VISION_MODEL)


def chat_completion(
    messages: List[Dict[str, Any]],
    *,
    model: Optional[str] = None,
    max_tokens: int = 4096,
    temperature: float = 0.0,
) -> str:
    """Call /chat/completions and return assistant text content."""
    url = f"{get_base_url()}/chat/completions"
    payload = {
        "model": model or get_chat_model(),
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    if not resp.ok:
        raise RuntimeError(f"DashScope API error {resp.status_code}: {resp.text[:500]}")
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def encode_image_file(image_path: Union[str, Path]) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def analyze_image_with_task(
    image_path: Union[str, Path],
    task: str,
    *,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Vision + reasoning for short-term memory (replaces GPT-4o vision)."""
    b64 = encode_image_file(image_path)
    messages = [
        {
            "role": "system",
            "content": (
                "As an image analysis expert, infer object states in the image. "
                "Output only the final summary as lines: object: state"
            ),
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "1. Describe this image.\n"
                        "2. From [Task], extract object-relevant details.\n"
                        "3. Match each object to one state: heated, cooked, sliced, cleaned, "
                        "dirty, filled, used up, off, on, opened, closed, none.\n"
                        f"4. Output only step 3 summary.\n\n[Task]: {task}"
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                },
            ],
        },
    ]
    url = f"{get_base_url()}/chat/completions"
    payload = {
        "model": model or get_vision_model(),
        "messages": messages,
        "max_tokens": 4096,
    }
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    if not resp.ok:
        raise RuntimeError(f"DashScope vision error {resp.status_code}: {resp.text[:500]}")
    return resp.json()

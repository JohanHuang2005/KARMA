"""Text embeddings for STM/RAG (paper: text-embedding-3-large)."""
from __future__ import annotations

from typing import Literal, Sequence

import numpy as np

Backend = Literal["auto", "openai", "dashscope", "local"]


def _local_encode(texts: Sequence[str], model_name: str) -> np.ndarray:
    from src.paths import ensure_hf_mirror

    ensure_hf_mirror()
    from sentence_transformers import SentenceTransformer

    fallback = "all-mpnet-base-v2" if "embedding-3" in model_name else model_name
    model = SentenceTransformer(fallback)
    return np.asarray(model.encode(list(texts), convert_to_tensor=False))


def encode_texts(
    texts: Sequence[str],
    *,
    model: str = "text-embedding-3-large",
    backend: Backend = "auto",
) -> np.ndarray:
    if not texts:
        return np.zeros((0, 0))

    from src.llm.client import embed_texts_openai_compatible

    if backend == "local":
        return _local_encode(texts, model)

    try:
        return embed_texts_openai_compatible(texts, model=model, backend=backend)
    except Exception:
        if backend == "auto":
            return _local_encode(texts, model)
        raise


def cosine_similarity(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    if matrix.size == 0:
        return np.array([])
    q = query / (np.linalg.norm(query) + 1e-8)
    m = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-8)
    return m @ q

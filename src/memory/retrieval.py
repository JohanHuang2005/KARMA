"""Short-term memory retrieval + experience RAG (KARMA paper Sec. IV-B/C)."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

import numpy as np

from src.memory.embeddings import cosine_similarity, encode_texts
from src.paths import resolve

if TYPE_CHECKING:
    from config import Config


def load_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().strip()


def extract_task(description: str) -> str | None:
    colon_index = description.find(":")
    if colon_index != -1:
        return description[colon_index + 1 :].split(".")[0].strip()
    return description.strip() or None


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_to_file(file_path, content):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def update_memory_with_state(memory_file, analysis_file):
    with open(memory_file, "r", encoding="utf-8") as file:
        memory_data = json.load(file)

    with open(analysis_file, "r", encoding="utf-8") as file:
        analysis_data = json.load(file)

    if not analysis_data:
        return
    last_analysis_key = list(analysis_data.keys())[-1]
    state_data = {obj.lower(): state for obj, state in analysis_data[last_analysis_key].items()}

    for item in memory_data:
        object_type = item.get("objectType", "").lower()
        if object_type in state_data:
            item["state"] = state_data[object_type]

    with open(memory_file, "w", encoding="utf-8") as file:
        json.dump(memory_data, file, ensure_ascii=False, indent=4)


def _memory_unit_text(item: dict) -> str:
    pos = item.get("position", {})
    state = item.get("state", "unknown")
    obj_id = item.get("objectId", item.get("objectType", "object"))
    return (
        f"Id: {obj_id}, Position: ({pos.get('x', 0):.2f}, {pos.get('y', 0):.2f}, "
        f"{pos.get('z', 0):.2f}), State: {state}"
    )


def _should_use_stm(query: str, items: list, threshold: float, cfg: "Config") -> tuple[bool, float]:
    if not items or not query:
        return False, 0.0
    unit_texts = [_memory_unit_text(item) for item in items]
    vecs = encode_texts(
        [query] + unit_texts,
        model=cfg.memory.embedding_model,
        backend=cfg.memory.embedding_backend,
    )
    scores = cosine_similarity(vecs[0], vecs[1:])
    best = float(np.max(scores)) if len(scores) else 0.0
    return best >= threshold, best


def run_memory_retrieval(config: "Config | None" = None) -> dict:
    from config import Config as C

    cfg = config or C()

    analysis_file_path = resolve("memory/analysis_results.json")
    memory_file_path = resolve("memory/memory3.json")
    example_file_path = resolve("experience/experience.json")
    examples_output_path = resolve("prompts/examples.txt")
    instruction_file_path = resolve("prompts/instruction.txt")
    short_term_memory_file_path = resolve("prompts/short_term_memory.txt")
    similarity_flag_path = resolve("logs/similarity_flag.json")

    update_memory_with_state(str(memory_file_path), str(analysis_file_path))
    items = load_json(str(memory_file_path))
    description = load_file(str(instruction_file_path))
    extracted_task = extract_task(description) or ""

    metrics: dict = {"stm_used": False, "best_similarity": 0.0, "stm_units": 0}

    if extracted_task and items:
        unit_texts = [_memory_unit_text(item) for item in items]
        vecs = encode_texts(
            [extracted_task] + unit_texts,
            model=cfg.memory.embedding_model,
            backend=cfg.memory.embedding_backend,
        )
        scores = cosine_similarity(vecs[0], vecs[1:])
        top_k = min(cfg.memory.stm_top_k, len(items))
        top_indices = np.argsort(scores)[::-1][:top_k]

        use_stm, best = _should_use_stm(extracted_task, items, cfg.memory.similarity_threshold, cfg)
        metrics["best_similarity"] = best
        metrics["stm_used"] = use_stm
        metrics["stm_units"] = top_k if use_stm else 0

        similarity_flag_path.parent.mkdir(parents=True, exist_ok=True)
        with open(similarity_flag_path, "w", encoding="utf-8") as f:
            json.dump({"similarity_flag": use_stm, "score": best}, f, indent=2)

        if use_stm:
            blocks = []
            for rank, idx in enumerate(top_indices, start=1):
                item = items[int(idx)]
                blocks.append(f"STM unit {rank}:\n{_memory_unit_text(item)}")
            save_to_file(str(short_term_memory_file_path), "\n\n".join(blocks))
        else:
            save_to_file(str(short_term_memory_file_path), "")

    example_data = load_json(str(example_file_path))
    tasks = [example["task"] for example in example_data]
    query_vec = encode_texts(
        [extracted_task or description],
        model=cfg.memory.embedding_model,
        backend=cfg.memory.embedding_backend,
    )[0]
    task_vecs = encode_texts(
        tasks,
        model=cfg.memory.embedding_model,
        backend=cfg.memory.embedding_backend,
    )
    rag_scores = cosine_similarity(query_vec, task_vecs)
    top_k_rag = min(cfg.memory.rag_top_k, len(example_data))
    top_indices = np.argsort(rag_scores)[::-1][:top_k_rag]
    top_decompositions = [example_data[int(idx)]["decomposition"] for idx in top_indices]

    with open(examples_output_path, "w", encoding="utf-8") as file:
        for i, decomposition in enumerate(top_decompositions):
            file.write(f"Example {i+1} Decomposition:\n")
            file.write("\n".join(decomposition))
            file.write("\n\n")

    return metrics


def main():
    run_memory_retrieval()


if __name__ == "__main__":
    main()

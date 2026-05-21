import json

import numpy as np
from sentence_transformers import SentenceTransformer, util

from src.paths import ensure_hf_mirror, resolve


def load_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().strip()


def extract_task(description):
    colon_index = description.find(":")
    if colon_index != -1:
        task = description[colon_index + 1 :].split(".")[0].strip()
        return task
    return None


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

    last_analysis_key = list(analysis_data.keys())[-1]
    state_data = {obj.lower(): state for obj, state in analysis_data[last_analysis_key].items()}

    for item in memory_data:
        object_type = item.get("objectType", "").lower()
        if object_type in state_data:
            item["state"] = state_data[object_type]

    with open(memory_file, "w", encoding="utf-8") as file:
        json.dump(memory_data, file, ensure_ascii=False, indent=4)


def main():
    analysis_file_path = resolve("memory/analysis_results.json")
    memory_file_path = resolve("memory/memory3.json")
    example_file_path = resolve("experience/experience.json")
    examples_output_path = resolve("prompts/examples.txt")
    instruction_file_path = resolve("prompts/instruction.txt")
    short_term_memory_file_path = resolve("prompts/short_term_memory.txt")

    update_memory_with_state(str(memory_file_path), str(analysis_file_path))
    items = load_json(str(memory_file_path))
    description = load_file(str(instruction_file_path))
    extracted_task = extract_task(description)

    if extracted_task:
        print(f"Extracted task: {extracted_task}")
    else:
        print("No task found.")
        extracted_task = ""

    if not extracted_task:
        return

    ensure_hf_mirror()
    model = SentenceTransformer("all-mpnet-base-v2")

    item_texts = [item["objectType"] for item in items]
    item_embeddings = model.encode(item_texts, convert_to_tensor=True)
    query_embedding = model.encode(extracted_task, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(query_embedding, item_embeddings)[0].cpu().numpy()

    top_result_idx = np.argsort(cosine_scores)[::-1][0]
    top_result_item = items[top_result_idx]
    print("Top matching item:")
    print(
        f"Object Type: {top_result_item['objectType']}, "
        f"Position: {top_result_item['position']}, "
        f"Score: {cosine_scores[top_result_idx]:.4f}"
    )

    position = top_result_item["position"]
    formatted_content = (
        f"{top_result_item['objectType']} is at position "
        f"({position['x']:.2f}, {position['y']:.2f}, {position['z']:.2f})."
    )
    save_to_file(str(short_term_memory_file_path), formatted_content)
    print(f"Top matching item has been saved to prompts/short_term_memory.txt")

    example_data = load_json(str(example_file_path))
    tasks = [example["task"] for example in example_data]
    task_embeddings = model.encode(tasks, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(query_embedding, task_embeddings)[0].cpu().numpy()
    top_k_indices = np.argsort(cosine_scores)[::-1][:3]
    top_decompositions = [example_data[idx]["decomposition"] for idx in top_k_indices]

    with open(examples_output_path, "w", encoding="utf-8") as file:
        for i, decomposition in enumerate(top_decompositions):
            file.write(f"Example {i+1} Decomposition:\n")
            file.write("\n".join(decomposition))
            file.write("\n\n")

    print("Top 3 task decompositions have been saved to prompts/examples.txt")


if __name__ == "__main__":
    main()

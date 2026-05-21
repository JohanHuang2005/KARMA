import json

from src.llm.client import chat_completion
from src.paths import LOGS_DIR, PROMPTS_DIR, RESOURCES_DIR, TASK_FUNCTIONS_PATH

similarity_flag_path = str(LOGS_DIR / "similarity_flag.json")
messages_path = str(LOGS_DIR / "messages.json")


def load_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


MARKER = "# --- LLM-generated task functions below ---"


def insert_code_into_file(new_code: str, target_file_path: str) -> None:
    with open(target_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    header: list[str] = []
    for line in lines:
        header.append(line)
        if MARKER in line:
            break

    with open(target_file_path, "w", encoding="utf-8") as file:
        file.writelines(header)
        if not header[-1].endswith("\n"):
            file.write("\n")
        file.write("\n")
        file.write(new_code.strip())
        file.write("\n")


def load_similarity_flag():
    try:
        with open(similarity_flag_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("similarity_flag", False)
    except FileNotFoundError:
        return False


def main():
    use_short_term_memory = load_similarity_flag()

    skills = load_file(str(PROMPTS_DIR / "skills.txt"))
    skills_ex = load_file(str(RESOURCES_DIR / "actions.py"))
    role = load_file(str(PROMPTS_DIR / "role.txt"))
    examples = load_file(str(PROMPTS_DIR / "examples.txt"))
    emphasize = load_file(str(PROMPTS_DIR / "emphasize.txt"))
    instruction = load_file(str(PROMPTS_DIR / "instruction.txt"))
    short_term_memory = load_file(str(PROMPTS_DIR / "short_term_memory.txt"))
    long_term_memory = load_file(str(PROMPTS_DIR / "long_term_memory.txt"))

    messages = [
        {"role": "user", "content": skills},
        {"role": "user", "content": skills_ex},
        {"role": "system", "content": role},
        {"role": "user", "content": examples},
        {"role": "user", "content": emphasize},
        {"role": "user", "content": long_term_memory},
        {"role": "user", "content": instruction},
    ]

    if use_short_term_memory:
        messages.insert(5, {"role": "user", "content": short_term_memory})

    with open(messages_path, "w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=4)

    response_content = chat_completion(messages, max_tokens=4096, temperature=0.0)

    lines = response_content.split("\n")
    code_lines = []
    recording = False
    function_name = None

    for line in lines:
        if line.strip().startswith("def "):
            recording = True
            function_name = line.split("(")[0].split()[1]
        if recording:
            if line.strip() == "```":
                continue
            code_lines.append(line)

    api_generated_code = "\n".join(code_lines).strip()
    print(api_generated_code)

    target_file_path = str(TASK_FUNCTIONS_PATH)
    insert_code_into_file(api_generated_code, target_file_path)

    with open(str(LOGS_DIR / "generated_function_name.json"), "w") as file:
        json.dump({"function_name": function_name}, file)


if __name__ == "__main__":
    main()

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def run_script(script_path: Path) -> None:
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        print(f"Output of {script_path.name}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path.name}:\n{e.stderr}")


print("Running query_with_short_term_memory (via src)...")
from src.memory.retrieval import main as run_retrieval

run_retrieval()

print("Running llm_as_planner (via src)...")
from src.llm.planner import main as run_planner

run_planner()

"""KARMA experiment pipeline: memory retrieval → LLM planning → simulation execution."""
from __future__ import annotations

import json
from pathlib import Path

from loguru import logger

from config import Config
from src.utils import log_metrics, save_run_metrics, show_config, timer, wandb_log
from src.paths import ensure_repo_cwd, ensure_runtime_dirs, resolve
from src.memory.retrieval import main as run_memory_retrieval
from src.llm.planner import main as run_planner


ROBOTS = [
    {
        "name": "robot1",
        "skills": [
            "GoToObject",
            "OpenObject",
            "CloseObject",
            "BreakObject",
            "SliceObject",
            "SwitchOn",
            "SwitchOff",
            "PickupObject",
            "PutObject",
            "DropHandObject",
            "ThrowObject",
            "PushObject",
            "PullObject",
        ],
    }
]


def _write_instruction(task: str) -> None:
    content = (
        f"Please help me decompose the following tasks: {task}. "
        "Please output only the generated code."
    )
    (resolve("prompts/instruction.txt")).write_text(content, encoding="utf-8")
    with open(resolve("logs/task_description.json"), "w", encoding="utf-8") as f:
        json.dump({"task_description": task}, f, ensure_ascii=False, indent=4)


@wandb_log
@show_config
@timer
def pipeline(config: Config) -> dict:
    ensure_repo_cwd()
    ensure_runtime_dirs()
    job = config.env.job_type

    if job == "smoke":
        from scripts.smoke_test import main as smoke_main

        raise SystemExit(smoke_main())

    if job == "benchmark":
        from src.benchmark.eval import run_benchmark

        metrics = run_benchmark(
            task_name=config.benchmark.task_name,
            output_path=str(config.benchmark.output_path),
        )
        log_metrics(config, metrics)
        return metrics

    if config.task.instruction:
        _write_instruction(config.task.instruction)

    if config.memory.use_short_term:
        logger.info("Running short-term memory retrieval + RAG")
        run_memory_retrieval()

    logger.info("Running LLM planner")
    run_planner()

    if config.task.skip_execution:
        logger.info("Planning complete (skip_execution=True)")
        return {"status": "planned"}

    logger.info("Executing generated plan in AI2-THOR")
    from src.env import executor

    executor.parse_and_execute_task(ROBOTS[0])

    metrics = {"status": "executed", "task": config.task.instruction}
    save_run_metrics(metrics)
    return metrics

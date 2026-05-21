from dataclasses import replace

from config.config import Config, base_config
from config import CONFIG

CONFIG["headless"] = (
    "Memory retrieval + LLM planning only (no simulation)",
    replace(
        base_config,
        env=replace(base_config.env, job_type="plan", group="headless"),
        task=replace(base_config.task, use_gui=False, skip_execution=True),
    ),
)

CONFIG["smoke"] = (
    "Component smoke tests",
    replace(
        base_config,
        env=replace(base_config.env, job_type="smoke", wandb_mode="disabled"),
    ),
)

from dataclasses import replace

from config.config import Config, base_config
from config import CONFIG

CONFIG["benchmark"] = (
    "Run built-in benchmark tasks",
    replace(
        base_config,
        env=replace(base_config.env, job_type="benchmark", group="benchmark"),
    ),
)

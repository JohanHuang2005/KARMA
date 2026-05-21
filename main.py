#!/usr/bin/env python3
"""KARMA unified entry point (MoETTA-style CLI)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("KARMA_ROOT", str(ROOT))
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tyro
from loguru import logger

from config import CONFIG, Config
from src.utils import setup_logger
from src.pipeline import pipeline


@logger.catch(reraise=True)
def main(config: Config) -> None:
    setup_logger(config.env.name or config.env.job_type)
    if config.task.use_gui:
        from src.env.gui import launch_gui

        launch_gui()
        return
    pipeline(config)


if __name__ == "__main__":
    print("Available configs:", list(CONFIG.keys()))
    main(tyro.extras.overridable_config_cli(CONFIG))

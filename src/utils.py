"""Logging, timing, and optional W&B integration for KARMA."""
from __future__ import annotations

import functools
import json
import os
import random
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
from loguru import logger

from config import Config
from src.paths import ARTIFACTS_DIR, ensure_runtime_dirs, load_dotenv, resolve


def configure_opencv_headless() -> None:
    """No-op OpenCV GUI calls when DISPLAY is unavailable (headless servers)."""
    import os

    if os.environ.get("DISPLAY"):
        return
    import cv2

    cv2.imshow = lambda *args, **kwargs: None  # type: ignore[assignment]
    cv2.waitKey = lambda *args, **kwargs: -1  # type: ignore[assignment]


def setup_logger(run_name: str = "karma") -> None:
    ensure_runtime_dirs()
    log_dir = resolve("artifacts/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_dir / f"{run_name}_{{time:YYYYMMDD_HHmmss}}.log",
        rotation="50 MB",
        retention="7 days",
        encoding="utf-8",
    )


def show_config(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(config: Config, *args, **kwargs):
        logger.info("Config:\n{}", config)
        return func(config, *args, **kwargs)

    return wrapper


def deterministic(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        random.seed(42)
        np.random.seed(42)
        return func(*args, **kwargs)

    return wrapper


def timer(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - t0
        logger.info("{} finished in {:.2f}s", func.__name__, elapsed)
        return result

    return wrapper


def wandb_log(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(config: Config, *args, **kwargs):
        if config.env.wandb_mode == "disabled":
            return func(config, *args, **kwargs)

        load_dotenv()
        import wandb

        api_key = os.environ.get("WANDB_API_KEY")
        base_url = os.environ.get("WANDB_BASE_URL")
        if api_key:
            wandb.login(key=api_key, host=base_url or None)
        wandb.init(
            project=config.env.project,
            name=config.env.name or config.env.job_type,
            group=config.env.group,
            notes=config.env.notes,
            tags=list(config.env.tags),
            config=_config_to_dict(config),
            mode=config.env.wandb_mode,
            job_type=config.env.job_type,
        )
        try:
            return func(config, *args, **kwargs)
        finally:
            wandb.finish()

    return wrapper


def _config_to_dict(config: Config) -> dict[str, Any]:
    from dataclasses import asdict

    return asdict(config)


def save_run_metrics(metrics: dict[str, Any], path: Path | None = None) -> Path:
    ensure_runtime_dirs()
    out = path or resolve("logs/run_metrics.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    logger.info("Metrics saved to {}", out)
    return out


def log_metrics(config: Config, metrics: dict[str, Any]) -> None:
    save_run_metrics(metrics)
    if config.env.wandb_mode != "disabled":
        import wandb

        if wandb.run is not None:
            wandb.log(metrics)

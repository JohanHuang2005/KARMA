from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from . import CONFIG


@dataclass
class EnvironmentConfig:
    project: str = "KARMA"
    group: str = ""
    name: str = ""
    notes: str = ""
    tags: tuple[str, ...] = ()
    local: bool = True
    job_type: Literal["plan", "execute", "benchmark", "smoke", "debug"] = "plan"
    wandb_mode: Literal["online", "offline", "disabled"] = "disabled"


@dataclass
class LLMConfig:
    chat_model: str = "gpt-4o"
    vision_model: str = "gpt-4o"
    max_tokens: int = 4096
    temperature: float = 0.0


@dataclass
class MemoryConfig:
    embedding_model: str = "text-embedding-3-large"
    embedding_backend: Literal["auto", "openai", "dashscope", "local"] = "auto"
    use_short_term: bool = True
    stm_top_k: int = 1
    rag_top_k: int = 3
    similarity_threshold: float = 0.3
    replacement_policy: Literal["fifo", "lfu", "wtinylfu"] = "fifo"
    max_stm_objects: int = 100


@dataclass
class SimulationConfig:
    scene: str = "FloorPlan1"
    floor: int = 1
    width: int = 1000
    height: int = 1000
    grid_size: float = 0.25
    quality: str = "Low"
    platform: Literal["CloudRendering", "Linux64"] = "CloudRendering"


@dataclass
class TaskConfig:
    instruction: str = ""
    task_id: str = ""
    use_gui: bool = False
    skip_execution: bool = False


@dataclass
class BenchmarkConfig:
    task_name: Literal[
        "long_task_1",
        "long_task_2",
        "long_task_3",
        "long_task_4",
        "long_task_5",
        "long_task_6",
        "alfred_l",
    ] = "long_task_3"
    alfred_l_category: Literal["all", "simple", "composite", "complex"] = "all"
    output_path: Path = field(default_factory=lambda: Path("artifacts/output.json"))


@dataclass
class Config:
    env: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    task: TaskConfig = field(default_factory=TaskConfig)
    benchmark: BenchmarkConfig = field(default_factory=BenchmarkConfig)


base_config = Config()
CONFIG["base"] = ("Default KARMA pipeline", base_config)

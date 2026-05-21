CONFIG: dict = {}

from .config import Config, base_config

from .subconfigs import benchmark, headless

__all__ = ["Config", "base_config", "CONFIG"]

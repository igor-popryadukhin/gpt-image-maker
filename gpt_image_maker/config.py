from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import List, Optional


@dataclasses.dataclass
class PromptTemplateConfig:
    template: Optional[str] = None
    template_file: Optional[Path] = None


@dataclasses.dataclass
class RetryConfig:
    download_retries: int = 3
    generation_retries: int = 5
    base_backoff: float = 1.0
    max_backoff: float = 60.0


@dataclasses.dataclass
class GenerationConfig:
    size: str = "1536x1024"
    quality: str = "high"
    format: str = "png"
    transparent_background: bool = True
    model: str = "gpt-image-1-mini"
    api_base_url: Optional[str] = None
    timeout: float = 60.0


@dataclasses.dataclass
class StateConfig:
    state_file: Path
    resume: bool = False
    reset_state: bool = False


@dataclasses.dataclass
class CLIConfig:
    input_file: Path
    output_root: Path
    prompt_template: PromptTemplateConfig
    retry: RetryConfig
    generation: GenerationConfig
    state: StateConfig
    delimiter: str = ","
    columns: Optional[List[str]] = None
    log_file: Optional[Path] = None
    log_level: str = "INFO"
    no_progress: bool = False
    preview: bool = False
    preview_timeout: int = 0
    ping_url: Optional[str] = None
    overwrite: bool = False


DEFAULT_COLUMNS = [
    "brand",
    "model",
    "production_period",
    "generation",
    "body_type",
    "image_url",
]

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from tqdm import tqdm

from .config import CLIConfig
from .downloader import download_image
from .generator import ImageGenerator
from .net import is_network_error, wait_for_network
from .paths import compute_output_path, ensure_parent_dir
from .prompt_builder import PromptBuilder
from .reader import InputReader
from .state import LineStatus, State
from .preview import show_preview

logger = logging.getLogger(__name__)


class Runner:
    def __init__(self, config: CLIConfig, api_key: str):
        self.config = config
        self.api_key = api_key

    def run(self) -> None:
        input_file = self.config.input_file
        state = self._prepare_state()
        prompt_template = self._load_prompt_template()
        builder = PromptBuilder(prompt_template)
        generator = ImageGenerator(self.config.generation, self.config.retry, api_key=self.api_key)

        reader = list(InputReader(input_file, delimiter=self.config.delimiter, columns=self.config.columns))
        total = len(reader)
        progress_iter = tqdm(reader, disable=self.config.no_progress, desc="Processing")

        for row in progress_iter:
            if row.line_number in state.statuses and state.statuses[row.line_number].status == "ok":
                continue
            output_path = compute_output_path(row.data["image_url"], self.config.output_root, extension="png")
            if output_path.exists() and not self.config.overwrite:
                state.statuses[row.line_number] = LineStatus(status="skip", message="exists")
                state.save(self.config.state.state_file)
                continue

            prompt = builder.build(row.data)
            download_path = download_image(row.data["image_url"], input_file.parent, self.config.retry)
            if not download_path:
                state.statuses[row.line_number] = LineStatus(status="error", message="download failed")
                state.save(self.config.state.state_file)
                continue

            image_bytes = generator.generate(prompt, download_path)
            if image_bytes is None:
                state.statuses[row.line_number] = LineStatus(status="error", message="generation failed")
                state.save(self.config.state.state_file)
                continue

            ensure_parent_dir(output_path)
            output_path.write_bytes(image_bytes)
            state.statuses[row.line_number] = LineStatus(status="ok")
            state.save(self.config.state.state_file)

            if self.config.preview:
                show_preview(download_path, output_path, timeout=self.config.preview_timeout)

    def _prepare_state(self) -> State:
        state_config = self.config.state
        existing = State.load(state_config.state_file)
        computed_hash = State.calculate_hash(self.config.input_file)
        if existing and not state_config.reset_state:
            if existing.input_hash == computed_hash:
                logger.info("Resuming from existing state file %s", state_config.state_file)
                return existing
        logger.info("Creating new state file %s", state_config.state_file)
        return State(input_file=self.config.input_file, input_hash=computed_hash)

    def _load_prompt_template(self) -> str:
        cfg = self.config.prompt_template
        if cfg.template_file:
            return Path(cfg.template_file).read_text(encoding="utf-8")
        if cfg.template:
            return cfg.template
        raise ValueError("Prompt template is required")

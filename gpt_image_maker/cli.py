from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .config import CLIConfig, GenerationConfig, PromptTemplateConfig, RetryConfig, StateConfig
from .logging_utils import setup_logging
from .runner import Runner


def parse_args(argv: list[str]) -> CLIConfig:
    parser = argparse.ArgumentParser(prog="gpt-image-maker", description="Batch generate images using OpenAI")
    parser.add_argument("--input-file", required=True, type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--prompt-template")
    parser.add_argument("--prompt-template-file", type=Path)
    parser.add_argument("--delimiter", default=",")
    parser.add_argument("--download-retries", type=int, default=3)
    parser.add_argument("--generation-retries", type=int, default=5)
    parser.add_argument("--size", default="1536x1024")
    parser.add_argument("--quality", default="high")
    parser.add_argument("--format", default="png")
    parser.add_argument("--transparent-background", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--model", default="gpt-image-1-mini")
    parser.add_argument("--api-base-url")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--log-file", type=Path)
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--no-progress", action="store_true")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--preview-timeout", type=int, default=0)
    parser.add_argument("--ping-url")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--reset-state", action="store_true")
    parser.add_argument("--state-file", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--download-only", action="store_true")

    args = parser.parse_args(argv)

    input_file: Path = args.input_file
    output_root = args.output_root or input_file.parent
    state_file = args.state_file or input_file.parent / ".gpt-image-maker.state.json"

    prompt_cfg = PromptTemplateConfig(template=args.prompt_template, template_file=args.prompt_template_file)
    retry_cfg = RetryConfig(
        download_retries=args.download_retries,
        generation_retries=args.generation_retries,
    )
    gen_cfg = GenerationConfig(
        size=args.size,
        quality=args.quality,
        format=args.format,
        transparent_background=args.transparent_background,
        model=args.model,
        api_base_url=args.api_base_url,
        timeout=args.timeout,
    )
    state_cfg = StateConfig(state_file=state_file, resume=args.resume, reset_state=args.reset_state)

    return CLIConfig(
        input_file=input_file,
        output_root=output_root,
        prompt_template=prompt_cfg,
        retry=retry_cfg,
        generation=gen_cfg,
        delimiter=args.delimiter,
        log_file=args.log_file,
        log_level=args.log_level,
        no_progress=args.no_progress,
        preview=args.preview,
        preview_timeout=args.preview_timeout,
        ping_url=args.ping_url,
        overwrite=args.overwrite,
        download_only=args.download_only,
        columns=None,
        state=state_cfg,
    )


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    config = parse_args(argv)
    setup_logging(config.log_level, config.log_file)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY environment variable is required")

    runner = Runner(config, api_key)
    try:
        runner.run()
    except Exception as exc:  # noqa: BLE001
        import logging

        logging.exception("Execution failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

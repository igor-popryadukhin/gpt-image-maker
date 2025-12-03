from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

from openai import OpenAI
from openai._exceptions import APIConnectionError, APIStatusError, RateLimitError

from .config import GenerationConfig, RetryConfig

logger = logging.getLogger(__name__)


class ImageGenerator:
    def __init__(self, generation: GenerationConfig, retry: RetryConfig, api_key: Optional[str] = None):
        self.generation = generation
        self.retry = retry
        kwargs = {}
        if generation.api_base_url:
            kwargs["base_url"] = generation.api_base_url
        if api_key:
            kwargs["api_key"] = api_key
        self.client = OpenAI(**kwargs)

    def generate(self, prompt: str, image_path: Path) -> Optional[bytes]:
        backoff = self.retry.base_backoff
        for attempt in range(1, self.retry.generation_retries + 1):
            try:
                with image_path.open("rb") as f:
                    result = self.client.images.generate(
                        model=self.generation.model,
                        prompt=prompt,
                        image=f,
                        size=self.generation.size,
                        quality=self.generation.quality,
                        response_format=self.generation.format,
                        transparent=self.generation.transparent_background,
                        timeout=self.generation.timeout,
                    )
                if not result.data:
                    raise RuntimeError("No data returned from generation")
                image_base64 = result.data[0].b64_json
                return self._decode_image(image_base64)
            except (APIConnectionError, APIStatusError, RateLimitError) as exc:
                logger.warning(
                    "Generation attempt %s/%s failed: %s", attempt, self.retry.generation_retries, exc
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("Unexpected generation error: %s", exc)
                break
            time.sleep(min(backoff, self.retry.max_backoff))
            backoff *= 2
        return None

    @staticmethod
    def _decode_image(data: str) -> bytes:
        import base64

        return base64.b64decode(data)

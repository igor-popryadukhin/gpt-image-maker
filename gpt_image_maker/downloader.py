from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

import requests

from .config import RetryConfig
from .paths import compute_temp_download_path, ensure_parent_dir

logger = logging.getLogger(__name__)


def download_image(image_url: str, input_file_dir: Path, retry: RetryConfig) -> Optional[Path]:
    temp_root = input_file_dir / "tmp"
    target = compute_temp_download_path(image_url, temp_root)
    ensure_parent_dir(target)

    backoff = retry.base_backoff
    for attempt in range(1, retry.download_retries + 1):
        try:
            resp = requests.get(image_url, timeout=30)
            resp.raise_for_status()
            target.write_bytes(resp.content)
            logger.info("Downloaded %s to %s", image_url, target)
            return target
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Download attempt %s/%s failed for %s: %s", attempt, retry.download_retries, image_url, exc
            )
            if attempt >= retry.download_retries:
                break
            time.sleep(min(backoff, retry.max_backoff))
            backoff *= 2
    return None

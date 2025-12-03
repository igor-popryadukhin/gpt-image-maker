from __future__ import annotations

import logging
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)


def wait_for_network(ping_url: str, backoff: float = 5.0, max_backoff: float = 60.0) -> None:
    delay = backoff
    while True:
        try:
            resp = requests.head(ping_url, timeout=5)
            if resp.ok:
                logger.info("Network restored via %s", ping_url)
                return
        except Exception:  # noqa: BLE001
            logger.warning("Network unavailable, retrying in %.1f seconds", delay)
        time.sleep(delay)
        delay = min(delay * 2, max_backoff)


def is_network_error(exc: Exception) -> bool:
    return isinstance(exc, (requests.ConnectionError, requests.Timeout))

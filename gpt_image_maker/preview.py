from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PIL import Image

logger = logging.getLogger(__name__)


def show_preview(original_path: Path, generated_path: Path, timeout: int = 0) -> None:
    try:
        original = Image.open(original_path)
        generated = Image.open(generated_path)
        width = original.width + generated.width
        height = max(original.height, generated.height)
        canvas = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        canvas.paste(original, (0, 0))
        canvas.paste(generated, (original.width, 0))
        canvas.show()
        if timeout > 0:
            import time

            time.sleep(timeout)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to show preview: %s", exc)

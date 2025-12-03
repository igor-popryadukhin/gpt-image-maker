from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.parse import urlparse


def compute_output_path(image_url: str, output_root: Path, extension: str = "png") -> Path:
    parsed = urlparse(image_url)
    url_path = parsed.path.lstrip("/")
    if not url_path:
        raise ValueError("Image URL missing path component")
    target = Path(output_root) / Path(url_path)
    return target.with_suffix(f".{extension}")


def compute_temp_download_path(image_url: str, temp_root: Path) -> Path:
    parsed = urlparse(image_url)
    filename = Path(parsed.path).name
    if not filename:
        digest = hashlib.sha256(image_url.encode("utf-8")).hexdigest()[:12]
        filename = f"image_{digest}"
    return temp_root / filename


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

import sys
import types

import pytest

if "requests" not in sys.modules:
    sys.modules["requests"] = types.SimpleNamespace(get=lambda *args, **kwargs: None)

from gpt_image_maker.config import RetryConfig
from gpt_image_maker.downloader import download_image


class DummyResponse:
    def __init__(self, content: bytes):
        self.content = content

    def raise_for_status(self):
        return None


def test_download_image_uses_existing_cache(monkeypatch, tmp_path):
    target = tmp_path / "cache" / "file.jpg"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"cached")

    called = False

    def fake_get(url, timeout):  # noqa: ARG001
        nonlocal called
        called = True
        raise RuntimeError("should not fetch")

    monkeypatch.setattr("requests.get", fake_get)
    retry = RetryConfig(download_retries=1)

    result = download_image("https://example.com/file.jpg", tmp_path, retry, target_path=target)

    assert result == target
    assert target.read_bytes() == b"cached"
    assert called is False


def test_download_image_overwrite(monkeypatch, tmp_path):
    target = tmp_path / "cache" / "file.jpg"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"old")

    def fake_get(url, timeout):  # noqa: ARG001
        return DummyResponse(b"new")

    monkeypatch.setattr("requests.get", fake_get)
    retry = RetryConfig(download_retries=1)

    result = download_image("https://example.com/file.jpg", tmp_path, retry, target_path=target, overwrite=True)

    assert result == target
    assert target.read_bytes() == b"new"

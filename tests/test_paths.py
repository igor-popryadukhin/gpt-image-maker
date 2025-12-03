from pathlib import Path

from gpt_image_maker.paths import compute_output_path, compute_temp_download_path


def test_compute_output_path_basic():
    url = "https://example.com/images/car.jpg"
    result = compute_output_path(url, Path("/root/out"))
    assert result == Path("/root/out/images/car.png")


def test_compute_temp_download_path_uses_filename():
    url = "https://example.com/images/car.jpg"
    temp_root = Path("/tmp")
    result = compute_temp_download_path(url, temp_root)
    assert result.name == "car.jpg"
    assert result.parent == temp_root

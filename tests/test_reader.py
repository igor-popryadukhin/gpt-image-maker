from pathlib import Path

import pytest

from gpt_image_maker.reader import InputReader, ParsedRow


def test_reader_parses_valid_lines(tmp_path: Path):
    content = '\n'.join([
        '"brand", "model", "period", "gen", "body", https://example.com/image.jpg',
    ])
    input_file = tmp_path / "input.txt"
    input_file.write_text(content, encoding="utf-8")

    rows = list(InputReader(input_file))
    assert len(rows) == 1
    row = rows[0]
    assert isinstance(row, ParsedRow)
    assert row.data["brand"] == "brand"
    assert row.data["image_url"] == "https://example.com/image.jpg"


def test_reader_invalid_url(tmp_path: Path):
    input_file = tmp_path / "input.txt"
    input_file.write_text('"brand", "model", "period", "gen", "body", image.jpg', encoding="utf-8")

    with pytest.raises(ValueError):
        list(InputReader(input_file))

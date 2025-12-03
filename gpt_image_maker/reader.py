from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .config import DEFAULT_COLUMNS

logger = logging.getLogger(__name__)


@dataclass
class ParsedRow:
    data: Dict[str, str]
    raw: str
    line_number: int


class InputReader:
    def __init__(self, path: Path, delimiter: str = ",", columns: Optional[List[str]] = None):
        self.path = path
        self.delimiter = delimiter
        self.columns = columns or DEFAULT_COLUMNS

    def __iter__(self) -> Iterable[ParsedRow]:
        with self.path.open("r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            for idx, row in enumerate(reader, start=1):
                raw_line = ",".join(row)
                if not row:
                    logger.debug("Skipping empty line %s", idx)
                    continue
                if len(row) < len(self.columns):
                    logger.error("Line %s has insufficient columns", idx)
                    raise ValueError(f"Line {idx} has insufficient columns: {row}")
                data = {col: row[i].strip().strip('"') for i, col in enumerate(self.columns)}
                image_url = data.get("image_url", "")
                if not image_url or not image_url.startswith(("http://", "https://")):
                    raise ValueError(f"Line {idx} has invalid image_url: {image_url}")
                yield ParsedRow(data=data, raw=raw_line, line_number=idx)

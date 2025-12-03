from __future__ import annotations

import dataclasses
import json
import logging
import tempfile
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class LineStatus:
    status: str
    message: Optional[str] = None


@dataclass
class State:
    input_file: Path
    input_hash: str
    statuses: Dict[int, LineStatus] = field(default_factory=dict)

    @classmethod
    def calculate_hash(cls, path: Path) -> str:
        digest = sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @classmethod
    def load(cls, path: Path) -> Optional["State"]:
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        statuses = {int(k): LineStatus(**v) for k, v in data.get("statuses", {}).items()}
        return cls(input_file=Path(data["input_file"]), input_hash=data["input_hash"], statuses=statuses)

    def save(self, path: Path) -> None:
        payload = {
            "input_file": str(self.input_file),
            "input_hash": self.input_hash,
            "statuses": {str(k): dataclasses.asdict(v) for k, v in self.statuses.items()},
        }
        with tempfile.NamedTemporaryFile("w", delete=False, dir=path.parent, encoding="utf-8") as tmp:
            json.dump(payload, tmp, indent=2, ensure_ascii=False)
            tmp_path = Path(tmp.name)
        tmp_path.replace(path)

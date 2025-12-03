from __future__ import annotations

from typing import Dict


class PromptBuilder:
    def __init__(self, template: str):
        self.template = template

    def build(self, values: Dict[str, str]) -> str:
        try:
            return self.template.format(**values)
        except KeyError as exc:
            missing = exc.args[0]
            raise KeyError(f"Missing placeholder '{missing}' for prompt template") from exc

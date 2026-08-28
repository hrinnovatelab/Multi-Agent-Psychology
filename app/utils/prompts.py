from __future__ import annotations

from pathlib import Path
from typing import Any


class PromptError(RuntimeError):
    pass


class PromptRepository:
    def __init__(self, root: Path = Path("prompts")) -> None:
        self.root = root

    def read(self, relative_path: str) -> str:
        path = (self.root / relative_path).resolve()
        if self.root.resolve() not in path.parents:
            raise PromptError("Prompt path escapes prompt directory")
        try:
            return path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise PromptError(f"Cannot read prompt {relative_path}: {exc}") from exc

    def compose(self, lens_prompt_path: str | None, phase: str, context: dict[str, Any]) -> str:
        parts = [
            self.read("shared/safety.md"),
            self.read("shared/epistemic_rules.md"),
            self.read("shared/output_rules.md"),
        ]
        if lens_prompt_path:
            parts.append(self.read(lens_prompt_path))
        parts.append(self.read(phase))
        parts.append("\nSTRUCTURED CONTEXT\n" + _json_context(context))
        return "\n\n---\n\n".join(parts)


def _json_context(context: dict[str, Any]) -> str:
    import json
    from enum import Enum

    return json.dumps(
        context,
        ensure_ascii=False,
        indent=2,
        default=lambda value: value.value if isinstance(value, Enum) else str(value),
    )

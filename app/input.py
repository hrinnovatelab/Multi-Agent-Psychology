from __future__ import annotations

import json
from pathlib import Path

from app.models import CaseRecord


class CaseInputError(ValueError):
    """Raised for an invalid or unsafe case input."""


def load_case(case_name: str, input_dir: Path = Path("input")) -> CaseRecord:
    base = input_dir.resolve()
    path = (base / case_name).resolve()
    if path.parent != base:
        raise CaseInputError("Case path must be a file directly inside the input directory")
    if path.suffix.lower() not in {".md", ".txt", ".json"}:
        raise CaseInputError("Case must use .md, .txt, or .json")
    if not path.is_file():
        raise CaseInputError(f"Case file not found: {case_name}")

    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        raise CaseInputError("Case file is empty")
    title = path.stem.replace("-", " ").strip().title()
    content = raw
    if path.suffix.lower() == ".json":
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CaseInputError(f"Invalid JSON case: {exc}") from exc
        if not isinstance(payload, dict):
            raise CaseInputError("JSON case must be an object")
        title = str(payload.get("title") or title)
        narrative = payload.get("narrative") or payload.get("content")
        if not isinstance(narrative, str) or not narrative.strip():
            raise CaseInputError("JSON case needs a non-empty 'narrative' or 'content'")
        questions = payload.get("questions", [])
        content = narrative.strip()
        if isinstance(questions, list) and questions:
            content += "\n\nLearner questions:\n" + "\n".join(f"- {q}" for q in questions)
    else:
        for line in raw.splitlines():
            if line.startswith("# "):
                title = line[2:].strip() or title
                break
    return CaseRecord(path.stem, title, content, str(path))

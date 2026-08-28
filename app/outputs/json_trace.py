from __future__ import annotations

import json
from pathlib import Path

from app.models import DebateState


def write_json_trace(path: Path, state: DebateState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

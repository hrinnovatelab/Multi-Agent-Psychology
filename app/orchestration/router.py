from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from app.models import DebateState, OutputMode
from app.outputs.filenames import artifact_stem
from app.outputs.json_trace import write_json_trace
from app.outputs.markdown import render_analyse, render_consulting, render_log


@dataclass(frozen=True, slots=True)
class OutputPaths:
    analyse: Path | None
    consulting: Path | None
    markdown_log: Path | None
    json_trace: Path | None


def route_outputs(
    state: DebateState,
    mode: OutputMode,
    timestamp: datetime,
    root: Path = Path("."),
    save_markdown: bool = True,
    save_json: bool = True,
) -> OutputPaths:
    stem = artifact_stem(state.case.name, timestamp)
    analyse_path = root / "analyse" / f"{stem}.md" if mode in {OutputMode.ANALYSE, OutputMode.BOTH} else None
    consulting_path = root / "consulting" / f"{stem}.md" if mode in {OutputMode.CONSULTING, OutputMode.BOTH} else None
    log_path = root / "logs" / f"{stem}.md" if save_markdown else None
    json_path = root / "logs" / f"{stem}.json" if save_json else None
    documents = (
        (analyse_path, render_analyse(state) if analyse_path else None),
        (consulting_path, render_consulting(state) if consulting_path else None),
        (log_path, render_log(state) if log_path else None),
    )
    for path, content in documents:
        if path is not None and content is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if json_path:
        write_json_trace(json_path, state)
    return OutputPaths(analyse_path, consulting_path, log_path, json_path)

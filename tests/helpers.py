from __future__ import annotations

from pathlib import Path

from app.config import load_config
from app.input import load_case
from app.models import OutputMode
from app.orchestration.runner import RunResult, run_critique
from app.providers.mock import MockProvider


async def run_mock(root: Path, mode: OutputMode = OutputMode.BOTH, rounds: int = 1) -> RunResult:
    return await run_critique(
        case=load_case("case.md", root / "input"),
        config=load_config(root / "config/settings.yaml", root / "config/agents.yaml"),
        provider=MockProvider(),
        mode=mode,
        rounds=rounds,
        root=root,
    )

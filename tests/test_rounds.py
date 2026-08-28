from pathlib import Path

import pytest

from app.cli import main
from tests.helpers import run_mock


@pytest.mark.asyncio
async def test_exact_debate_rounds(project_root: Path) -> None:
    result = await run_mock(project_root, rounds=5)
    starts = [event for event in result.state.events if event.event == "ROUND_STARTED"]
    assert result.state.round_number == 5
    assert len(starts) == 5


def test_cli_round_override(project_root: Path) -> None:
    exit_code = main(
        [
            "criticize",
            "--case",
            "case.md",
            "--rounds",
            "4",
            "--mode",
            "analyse",
            "--provider",
            "mock",
            "--root",
            str(project_root),
        ]
    )
    assert exit_code == 0
    completed = sorted((project_root / "checkpoints").glob("*-completed.json"))
    assert '"round_number": 4' in completed[-1].read_text(encoding="utf-8")

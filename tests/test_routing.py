from pathlib import Path

import pytest

from app.models import OutputMode
from tests.helpers import run_mock


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("mode", "analyse", "consulting"),
    [
        (OutputMode.ANALYSE, True, False),
        (OutputMode.CONSULTING, False, True),
        (OutputMode.BOTH, True, True),
    ],
)
async def test_output_modes(project_root: Path, mode: OutputMode, analyse: bool, consulting: bool) -> None:
    result = await run_mock(project_root, mode=mode)
    assert (result.outputs.analyse is not None) is analyse
    assert (result.outputs.consulting is not None) is consulting
    if mode is OutputMode.BOTH:
        assert result.outputs.analyse.read_text() != result.outputs.consulting.read_text()

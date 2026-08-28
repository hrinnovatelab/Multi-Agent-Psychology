from pathlib import Path

import pytest

from tests.helpers import run_mock


@pytest.mark.asyncio
async def test_complete_mocked_run_without_api_key(project_root: Path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = await run_mock(project_root, rounds=2)
    assert result.state.intake is not None
    assert len(result.state.analyses) == 8
    assert result.state.round_number == 2
    assert result.state.validation_results
    assert result.state.synthesis is not None
    assert all(path and path.exists() for path in (result.outputs.analyse, result.outputs.consulting, result.outputs.markdown_log, result.outputs.json_trace))
    events = {event.event for event in result.state.events}
    assert {"RUN_STARTED", "INTAKE_COMPLETED", "CLAIM_CREATED", "VALIDATION_COMPLETED", "RUN_COMPLETED"} <= events

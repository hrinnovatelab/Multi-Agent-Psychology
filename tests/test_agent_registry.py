from pathlib import Path

import pytest
import yaml

from tests.helpers import run_mock


@pytest.mark.asyncio
async def test_disabled_agent_does_not_participate(project_root: Path) -> None:
    path = project_root / "config/agents.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    payload["agents"]["jung"]["enabled"] = False
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    result = await run_mock(project_root)
    assert "jung" not in result.state.enabled_agents
    assert "jung" not in result.state.analyses
    assert all(item.critic_agent != "jung" and item.target_agent != "jung" for item in result.state.critiques)

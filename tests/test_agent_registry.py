from pathlib import Path

import pytest
import yaml

from app.agents import (
    EpistemicValidatorAgent,
    IntakeAgent,
    SynthesizerAgent,
    build_psychology_agents,
)
from app.config import ConfigurationError, load_config
from app.providers.mock import MockProvider
from app.utils.prompts import PromptError, PromptRepository
from tests.helpers import run_mock


EXPECTED_PANEL = (
    "freud",
    "jung",
    "skinner",
    "rogers",
    "beck",
    "bowlby",
    "frankl",
    "ellis",
)


def test_default_panel_builds_each_designed_psychology_agent(project_root: Path) -> None:
    config = load_config(project_root / "config/settings.yaml", project_root / "config/agents.yaml")
    prompts = PromptRepository(project_root / "prompts")

    agents = build_psychology_agents(config.agents, MockProvider(), config.runtime.retries, prompts)

    assert tuple(agents) == EXPECTED_PANEL
    assert len({agent.display_name for agent in agents.values()}) == len(EXPECTED_PANEL)
    for key, agent in agents.items():
        assert agent.key == key
        assert agent.prompt_path == f"psychology/{key}.md"
        lens_prompt = prompts.read(agent.prompt_path)
        assert "## Identity and scope" in lens_prompt
        assert "## What this lens examines" in lens_prompt
        assert "## Evidence priorities" in lens_prompt
        assert "## Required boundaries" in lens_prompt
        assert "## Characteristic blind spot to disclose" in lens_prompt


def test_system_agents_have_distinct_non_persona_roles() -> None:
    provider = MockProvider()
    assert IntakeAgent(provider, 0).role_name == "intake"
    assert EpistemicValidatorAgent(provider, 0).role_name == "epistemic_validator"
    assert SynthesizerAgent(provider, 0).role_name == "synthesizer"


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


def test_agent_prompt_path_cannot_escape_prompt_directory(project_root: Path) -> None:
    path = project_root / "config/agents.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    payload["agents"]["freud"]["prompt_path"] = "../secrets.md"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    with pytest.raises(ConfigurationError, match="prompt_path"):
        load_config(project_root / "config/settings.yaml", path)


def test_enabled_agent_requires_its_prompt_file(project_root: Path) -> None:
    path = project_root / "config/agents.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    payload["agents"]["freud"]["prompt_path"] = "psychology/missing.md"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    config = load_config(project_root / "config/settings.yaml", path)

    with pytest.raises(PromptError, match="missing.md"):
        build_psychology_agents(
            config.agents,
            MockProvider(),
            config.runtime.retries,
            PromptRepository(project_root / "prompts"),
        )

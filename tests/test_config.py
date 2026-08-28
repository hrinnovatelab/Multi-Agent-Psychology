from pathlib import Path

import pytest
import yaml

from app.config import ConfigurationError, load_config


def test_valid_config_loads(project_root: Path) -> None:
    config = load_config(project_root / "config/settings.yaml", project_root / "config/agents.yaml")
    assert config.debate.rounds == 3
    assert len([agent for agent in config.agents if agent.enabled]) == 8


def test_invalid_rounds_fail_clearly(project_root: Path) -> None:
    path = project_root / "config/settings.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    payload["debate"]["rounds"] = 0
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    with pytest.raises(ConfigurationError, match="at least 1"):
        load_config(path, project_root / "config/agents.yaml")
